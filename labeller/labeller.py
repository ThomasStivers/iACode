# labeler.py
# Copyright (C) 2017 Thomas Stivers

import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--building", default="TLR", help="The building to generate labels for.")
parser.add_argument("-c", "--columns", default=6, help="The number of columns to use when generating labels.")
parser.add_argument("-e", "--expression", default=None, help="A regular expression to limit the labels returned.")
parser.add_argument("-V", "--version", action="version", version="2017.10")

class Label:
	"""Represents a location label for a DS warehouse."""
	def __init__(self, type=None, aisle=None, bay=None, level=None, slot=None, building=None, separator="-"):
		self.building = building
		self.separator = separator
		self.type = type
		self.aisle = aisle
		self.bay = bay
		self.level = level
		self.slot = slot

	def __str__(self):
		"""Diferent buildings have different format templates for their labels. This function returns a human readable string customized for the building."""
		if self.building == "TLR":
			template = "{building}{separator}{aisle:02d}{separator}{bay:02d}{separator}{level}{separator}{slot:02d}"
		elif self.building in ("AF", "402", "MC", "225", "BULK", "220"):
			template = "{building}{separator}{type}{separator}{aisle:02d}{separator}{bay:02d}{separator}{slot}"
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
	"""This class has a generator to create lists of labels with the specific conditions for a given building."""
	def __init__(self, columns=6):
		"""When a Labels object is converted to a string it can have one or multiple columns."""
		self.columns = columns

	def __str__(self):
		"""Makes a string representation of multiple labels with the given number of columns."""
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
		"""Creates the list of labels for a given building, but only if the labels match the regular expression."""
		if expression != None:
			regexp = re.compile(expression, re.IGNORECASE)
		if building == "TLR":
			maxAisle = 70 # There are no more than 70 aisles in the building.
			maxBay = 40 # there are never more than 40 bays on an aisle.
			maxLevel = "E" # for aisles 1-49 there are 5 levels. We'll handle 50+ later.
			maxSlot = 2 # Each bay has 2 pallets side by side.

			for aisle in xrange(1,maxAisle+1): # Loop over all the aisles.
				if aisle < 3: # Aisles 1 and 2 stop at bay 32.
					maxBay = 32
				elif aisle > 49: # And aisles 50-70 stop at bay 25.
					maxBay = 25
					maxLevel = "H" # But they have 8 levels instead of 5.
				else:
					maxBay = 40 # Reset to the most common aisle length.
					maxLevel = "E" # and the most common number of levels.
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
							self.append(l)


if __name__ == "__main__":
	args = parser.parse_args()
	taylor = Labels(int(args.columns))
	taylor.generate(args.building, args.expression)
	print taylor