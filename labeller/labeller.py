# labeler.py
# Copyright (C) 2017 Thomas Stivers

import os
import re
import argparse
import barcode

parser = argparse.ArgumentParser()
parser.add_argument(
	"-b", "--building",
	help="The building to generate labels for.")
parser.add_argument(
	"-c", "--columns", default=6,
	help="The number of columns to use when generating labels.")
parser.add_argument(
	"-e", "--expression", default=None,
	help="A regular expression to limit the labels returned.")
parser.add_argument(
	"-V", "--version", action="version", version="2017.10")

class Label:
	"""Represents a location label for a DS warehouse."""
	def __init__(
		self, type=None, aisle=None, bay=None, level=None, slot=None,
		building=None, separator="-"):
		self.building = building
		self.separator = separator
		self.type = type
		self.aisle = aisle
		self.bay = bay
		self.level = level
		self.slot = slot

	def __str__(self):
		"""Diferent buildings have different format templates for their labels.
		
		This function returns a human readable string customized for the building."""
		# the convention for the Taylor building is "TLR-AISLE-BAY-LEVEL-SLOT".
		if self.building == "TLR":
			template = "\
{building}{separator}\
{aisle:02d}{separator}\
{bay:02d}{separator}\
{level}{separator}\
{slot:02d}"
		# The form for AF, MC, and Bulk is "BUILDING-TYPE-AISLE-BAY-SLOT".
		elif self.building in ("AF", "402", "MC", "225", "BULK", "220"):
			template = "\
{building}{separator}\
{type}{separator}\
{aisle:02d}{separator}\
{bay:02d}{separator}\
{slot}"
		return template.format(
			building=self.building,
			separator=self.separator,
			level=self.level,
			type=self.type,
			aisle=self.aisle,
			bay=self.bay,
			slot=self.slot
		)

class Labels(list):
	"""List with generator to create  labels with conditions for a building."""
	def __init__(self, columns=6):
		"""Create a new empty list of labels.
			
			When a Labels object is converted to a string it can have one or
			multiple columns."""
		self.columns = columns

	def __str__(self):
		"""Makes a string of multiple labels divided into columns."""
		lines = []
		line = []
		for i in xrange(0, len(self), self.columns):
			line = []
			for j in xrange(i, i+self.columns):
				try:
					line.append(str(self[j]))
				except(IndexError):
					pass
				j += 1
			lines.append(",".join(line))
		return "\n".join(lines)

	def generate(self, building, expression=None):
	
		"""Creates the list of labels for a building.
			
			If expression is included labels are generated only if the labels
			match the regular expression."""
			
		# We will do a lot of matching, so if we have an expression we should
		# compile it.
		if expression != None:
			regexp = re.compile(expression, re.IGNORECASE)

		# Apply the conditions for Taylor.
		if building == "TLR":
			# There are no more than 70 aisles in the building.
			maxAisle = 70
			# there are never more than 40 bays on an aisle.
			maxBay = 40
			# for aisles 1-49 there are 5 levels. We'll handle 50+ later.
			maxLevel = "E"
			# Each bay has 2 pallets side by side.
			maxSlot = 2

			# Loop over all the aisles.
			for aisle in xrange(1,maxAisle+1):
				# The conditions before the start of the inner loop can set
				# the starting and ending bays on an aisle.
				# Aisles 1 and 2 stop at bay 32.
				if aisle < 3: maxBay = 32
				# And aisles 50-70 stop at bay 25 and have levels A-H.
				elif aisle > 49: 
					maxBay = 25
					maxLevel = "H"
				else:
					# Reset to defaults.
					maxBay = 40
					maxLevel = "E"
				# For each aisle loop over all the bays.
				for bay in xrange(1,maxBay+1):
					# For each bay loop over all the levels.
					for level in xrange(ord("A"), ord(maxLevel)+1):
						# For each level of each bay on each aisle loop over both slots.
						for slot in xrange(1, maxSlot+1):
							# There are floor level tunnels at bays 20 and 33
							# that are 2 levels high.
							if (bay == 20 or bay == 33) and level < ord("C"): continue
							# Build the label.
							l = Label(
								aisle=aisle,
								bay=bay,
								level=chr(level),
								slot=slot,
								building=building
							)
							# If we have an expression that doesn't match we
							# do not add the label to the list.
							if ("regexp" in locals()) and\
								(regexp.search(str(l)) == None): continue
							self.append(l)

		# Apply the conditions for the AF building.
		if building in ("AF", "402"):
			floor = "F"
			rack = "R"
			shelf = "S"
			mezannine = "M"
			pallets = [floor, rack]
			boxes = [shelf, mezannine]
			building = "402"
			# There are no more than 28 aisles in S and M locations.
			maxAisle = 28
			# There are a few exceptions that start at 0, so we need a
			# variable minimum.
			minBay = 1 
			# there are never more than 40 bays on an aisle.
			maxBay = 40
			# The types of location at AF.
			types = [floor, mezannine, shelf, rack]
			# List of possible slot letters at AF.
			slots = list("ABCDEFGH")

			# Loop over all the location types.
			for type in types:
				# Coditions that apply to any type of location go here. The
				# conditions become more specific within the inner loops.
				if type == floor:
					# Floor locations only have slots A and B.
					slots = list("AB")
				if type in pallets:
					# Aisle 23 and bay 18 is the highest pallet aisle and bay
					# possible at AF.
					maxAisle = 23
					maxBay = 18
				elif type in boxes:
					# Aisle 28 bay 40 is the highest box only aisle and bay.
					maxAisle=28
					maxBay = 40
				for aisle in xrange(0,maxAisle+1):
					# Loop over all the aisles of each type. Here we apply
					# conditions specific to a given aisle.
					if type in pallets:
						# Pallet locations on aisle 0 have only 7 bays. There
						# are gaps in this aisle, but the bay numbers don't skip them.
						if aisle == 0: maxBay = 7
						# Aisles 6-8 stop at bay 14 to leave space for loading
						# and unloading trucks.
						elif aisle in [6, 7, 8]: maxBay = 14
						# Aisle 23 only has 3 bays with unnumbered gaps.
						elif aisle == 23: maxBay = 3
						# Fall back to a default of 18 bays per aisle.
						else: maxBay = 18
						# Now we set conditions for the minimum bay numbers.
						if aisle in [1, 22]: minBay = 0;
						elif aisle in [11, 15, 16]: minBay = 5
						elif aisle in [12, 13, 14]: minBay = 6
						else: minBay = 1
						# Aisles 21 and 22 have double-height picking locations.
						if aisle in [21, 22] and type == floor: slots = list("ABCD")
					# Conditions that apply to the shelves and mezannine.
					elif type in boxes:
						# Most of the selves have 3 levels with 2 slots on each.
						slots = list("ABCDEF")
						# There are no 0 bays in the shelves.
						minBay = 1
						# But aisle 3 does start at bay 4.
						if aisle == 3: minBay = 4
						# Aisle 0 is double length and folded in half allowing
						# for 23 bays.
						if aisle == 0: maxBay = 23
						# Aisles 1-2 go from the office to the loading dock.
						elif aisle in [1, 2]: maxBay = 24
						# Aisles 3-16 stop before the LTL shipping area.
						elif aisle in xrange(3, 16): maxBay = 11
						# Aisles 17-18 are the same length as aisles 1-2.
						if aisle in [17, 18]: maxBay = 25
						# Aisle 19 is a stand-alone aisle at the end of the offices.
						elif aisle == 19: maxBay = 12
						# For historical reasons aisles 20-27 do not exist.
						elif aisle in xrange(20, 27): continue
						# Aisles 27-28 extend the full length of the building.
						elif aisle in [27, 28]: maxBay = 40
						# Aisles 0 and 27 hold coats and only have 4 slots per
						# bay.
						if aisle in [0, 27]: slots = list("ABCD")
						# Only in the mezannine aisle 28 has double-wide shelf
						# locations allowing for only 3 slots per bay.
						if aisle == 28 and type == mezannine: slots = list("ABC")
					# Loop over all the bays on each aisle.
					for bay in xrange(minBay, maxBay+1):
						if type in pallets:
							# There is a floor-level tunnel at bay 10 for
							# aisles 1-21.
							if bay == 10 and (type == floor or aisle != 22): continue
							if bay == 17: continue
						if type in boxes:
							if bay == 0: continue
							if type == "M" and aisle == 0: continue
						# For each type of each bay on each aisle loop over all slots.
						for slot in slots:
							# Finally we set the label.
							l = Label(type=type, aisle=aisle, bay=bay, slot=slot, building=building)
							# If the label doesn't match the regular expression we will skip it.
							if ("regexp" in locals())\
								and (regexp.search(str(l)) == None): continue
							self.append(l)

		# Conditions for the MC building.
		if building in ("MC", "225"):
			floor = list("DF")
			rack = list("RU")
			shelf = "S"
			pallets = floor + rack
			boxes = [shelf]
			building = "225"
			minAisle = 0
			maxAisle = 72 # There are no more than 72 aisles.
			minBay = 1 # There are a few exceptions that start at 0.
			maxBay = 72 # there are never more than 40 bays on an aisle.
			types = list("DFRSU") # The types of location at MC.
			slots = list("ABCDEF") # The highest slot letter encountered at MC.

			for type in types: # Loop over all the location types.
				if type in list("FR"): # Floor locations only have slots A and B.
					slots = list("AB")
					minAisle = 1
					maxAisle = 72
					if type == list("RU"): slots = list("ABCDEFGH")
				elif type in list("DU"):
					maxAisle = 8
					minAisle = 4
				elif type in boxes:
					maxAisle=22
					maxBay = 18
				for aisle in xrange(minAisle,maxAisle+1): # Loop over all the aisles of each type.
					# print type, aisle, minAisle, maxAisle
					if type in pallets:
						if aisle == 0: continue
						if type == "D":
							minAisle = 4
							maxAisle = 8
							minBay = maxBay = 1
							slots = list("ABC")
						else:
							minAisle = 1
							maxAisle = 72
							minBay = 1
							maxBay = 72
							slots = list("AB")
							if aisle in range(1,11): minBay = 5
							if aisle in range(1, 9): maxBay = 46
							if aisle in range(8,11): maxBay = 72
							elif aisle in range(11, 73): maxBay = 6
					elif type in boxes:
						slots = list("ABCDEF")
						minBay = 1
					for bay in xrange(minBay, maxBay+1): # For each bay loop over all the levels.
						if type == "F":
							if bay in [8, 25, 33, 47]: continue
						if type == "R": slots = list("ABCDEFGH")
						if type in boxes:
							if bay == 0: continue
						for slot in slots: # For each type of each bay on each aisle loop over all slots.
							l = Label(type=type, aisle=aisle, bay=bay, slot=slot, building=building)
							if ("regexp" in locals()) and (regexp.search(str(l)) == None):
								continue
							self.append(l)

	def makeBarcodes(self):
		"""Generate an HTML table which links to all the locations as barcode images."""
		import xml.etree.ElementTree as et
		from xml.dom import minidom
		
		html = et.Element("html")
		head = et.SubElement(html, "head")
		title = et.SubElement(head, "title")
		title.text = "Barcode Labels for {0}".format(self[0].building)
		style = et.SubElement(head, "style", {"type": "text/css"})
		style.text = """
			td img {
			  width: 3.5in;
			  height: 1.75in;
			  text-align: center;
			  vertical-align: center;
			}
		"""
		body = et.SubElement(html, "body")
		h1 = et.SubElement(body, "h1")
		h1.text = title.text
		table = et.SubElement(body, "table")
		i = 0
		for label in self:
			code = barcode.Code39(str(label), add_checksum=False)
			fileName = os.path.join("barcodes", str(label))
			# if not os.path.exists(fileName):
			code.save(fileName, {"font_size": 16})
			if i % self.columns == 0:
				tr = et.SubElement(table, "tr")
			td = et.SubElement(tr, "td")
			img = et.SubElement(td, "img",
				{"src": fileName + ".svg",
				"alt": str(label)
			})
			i += 1
		return minidom.parseString(et.tostring(html)).toprettyxml(indent="  ")

if __name__ == "__main__":
	args = parser.parse_args()
	labels = Labels(int(args.columns))
	labels.generate(args.building, args.expression)
	barcodes = labels.makeBarcodes()
	print barcodes