# labeler.py
# Copyright (C) 2017 Thomas Stivers

import re
import argparse

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
		import textwrap
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
				for bay in xrange(1,maxBay+1): # For each aisle loop over all the bays.
					for level in xrange(ord("A"), ord(maxLevel)+1): # For each bay loop over all the levels.
						for slot in xrange(1, maxSlot+1): # For each level of each bay on each aisle loop over both slots.
							if (bay == 20 or bay == 33) and level < ord("C"): # There are floor level tunnels at bays 20 and 33 that are 2 levels high.
								continue
							l = Label(aisle=aisle, bay=bay, level=chr(level), slot=slot, building=building)
							if ("regexp" in locals()) and (regexp.search(str(l)) == None):
								continue
							self.append(l)

		if building in ("AF", "402"):
			floor = "F"
			rack = "R"
			shelf = "S"
			mezannine = "M"
			pallets = [floor, rack]
			boxes = [shelf, mezannine]
			building = "402"
			maxAisle = 28 # There are no more than 28 aisles in S and M locations.
			minBay = 1 # There are a few exceptions that start at 0.
			maxBay = 40 # there are never more than 40 bays on an aisle.
			types = list("FMRS") # The types of location at AF.
			slots = list("ABCDEFGH") # The highest slot letter encountered at AF.

			for type in types: # Loop over all the location types.
				if type == floor: # Floor locations only have slots A and B.
					slots = list("AB")
				if type in pallets:
					maxAisle = 23
					maxBay = 18
				elif type in boxes:
					maxAisle=28
					maxBay = 40
				for aisle in xrange(0,maxAisle+1): # Loop over all the aisles of each type.
					if type in pallets:
						if aisle == 0: maxBay = 7
						elif aisle in [6, 8]: maxBay = 14
						elif aisle == 23: maxBay = 3
						else: maxBay = 18
						if aisle in [1, 22]: minBay = 0;
						elif aisle in [11, 15, 16]: minBay = 5
						elif aisle in [12, 13, 14]: minBay = 6
						else: minBay = 1
						if aisle == 22 and type == floor: slots = list("ABCD")
					elif type in boxes:
						slots = list("ABCDEF")
						minBay = 1
						if aisle == 0:
							maxBay = 23
							slots = list("ABCD")
						elif aisle in [1, 2]: maxBay = 25
						elif aisle in xrange(3, 16): maxBay = 11
						if aisle in [17, 18]: maxBay = 25
						elif aisle == 19: maxBay = 12
						elif aisle in xrange(20, 27): continue
						elif aisle in [27, 28]: maxBay = 40
						if aisle == 27: slots = list("ABCD")
						if aisle == 28: slots = list("ABC")
					for bay in xrange(minBay, maxBay+1): # For each bay loop over all the levels.
						if type in pallets:
							if bay == 10 and (type == floor or aisle == 22): continue
							if bay == 17: continue
						if type in boxes:
							if bay == 0: continue
							if type == "M" and aisle == 0: continue
						for slot in slots: # For each type of each bay on each aisle loop over all slots.
							l = Label(type=type, aisle=aisle, bay=bay, slot=slot, building=building)
							if ("regexp" in locals()) and (regexp.search(str(l)) == None):
								continue

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

if __name__ == "__main__":
	args = parser.parse_args()
	labels = Labels(int(args.columns))
	labels.generate(args.building, args.expression)
	print labels