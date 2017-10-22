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

	def __init__(self, aisle, bay, level, slot, building, separator="-"):
		self.building = building
		self.separator = separator
		self.aisle = aisle
		self.bay = bay
		self.level = level
		self.slot = slot

	def __str__(self):
		if self.building == "TLR":
			template = "{prefix}{separator}{aisle:02d}{separator}{bay:02d}{separator}{level}{separator}{slot:02d}"
			return template.format(
				prefix=self.building,
				separator=self.separator,
				aisle=self.aisle,
				bay=self.bay,
				level=self.level,
				slot=self.slot
			)

class Labels(list):
	def __init__(self, columns=6):
		self.columns = columns

	def __str__(self):
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

if __name__ == "__main__":
	args = parser.parse_args()
	taylor = Labels(int(args.columns))
	taylor.generate(args.building, args.expression)
	print taylor