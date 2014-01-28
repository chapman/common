#!/usr/bin/env python
#
# A module to analyze and identify any common problems which can be determined from log files
#
# Initial code by Andrew Chapman (chapman@skymount.com), 16th Jan 2014
#


# some logging oddities noticed while doing this, to be followed up on:
#   - tradheli MOT labels Mot1,Mot2,Mot3,Mot4,GGain
#   - Pixhawk doesn't output one of the FMT labels... forget which one
#   - MAG offsets seem to be constant (only seen data on Pixhawk)
#   - MAG offsets seem to be cast to int before being output? (param is -84.67, logged as -84)


# TODO: output log stats: size (kb/mb), length (lines), duration (using first and last GPS times)


import DataflashLog

import pprint  # temp
import imp
import glob
import inspect
import os, sys
import argparse


class TestResult:
	'''all tests pass back a standardized result'''
	class StatusType:
		# NA means not applicable for this log (e.g. copter tests against a plane log), UNKNOWN means it is missing data required for the test
		PASS, FAIL, WARN, UNKNOWN, NA = range(5)
	status = None
	statusMessage = ""
	extraFeedback = ""


class Test:
	'''base class to be inherited by each specific log test. Each test should be quite granular so we have lots of small tests with clear results'''
	name = ""
	result = None   # will be an instance of TestResult after being run
	def run(self, logdata):
		pass


class TestSuite:
	'''registers test classes'''
	tests   = []
	logfile = None
	logdata = None

	def __init__(self):
		# load in Test subclasses from the 'tests' folder
		dirName = os.path.dirname(os.path.abspath(__file__))
		testScripts = glob.glob(dirName + '/tests/*.py')
		testClasses = []
		for script in testScripts:
			m = imp.load_source("m",script)
			for name, obj in inspect.getmembers(m, inspect.isclass):
				if name not in testClasses and inspect.getsourcefile(obj) == script:
					testClasses.append(name)
					self.tests.append(obj())

		# and here's an example of explicitly loading a Test class
		# m = imp.load_source('TestBadParams', dirName + '/tests/TestBadParams.py')
		# self.tests.append(m.TestBadParams())


	def run(self, logdata):
		self.logdata = logdata
		self.logfile = logdata.filename
		# TODO: gather computation time when we run the tests
		for test in self.tests:
			test.run(self.logdata)

	def outputPlainText(self):
		print 'Dataflash log analysis report for file: ' + self.logfile + '\n'
		if self.logdata.vehicleType == "ArduCopter" and self.logdata.getCopterType():
			print 'Vehicle Type: %s (%s)' % (self.logdata.vehicleType, self.logdata.getCopterType())
		else:
			print 'Vehicle Type: %s' % self.logdata.vehicleType
		print 'Firmware Version: %s (%s)' % (self.logdata.firmwareVersion, self.logdata.firmwareHash)
		print 'Hardware: %s' % self.logdata.hardwareType
		print 'Free RAM: %s' % self.logdata.freeRAM
		print '\n'

		#print 'Formats:\n'
		#pprint.pprint(self.logdata.formats, width=1)
		#print '\n'
		#print 'Parameters:\n'
		#pprint.pprint(self.logdata.parameters, width=1)
		#print '\n'
		
		print "Test Results:"
		for test in self.tests:
			if test.result.status == TestResult.StatusType.PASS:
				print "  %20s:  PASS       %-50s" % (test.name, test.result.statusMessage)
			elif test.result.status == TestResult.StatusType.FAIL:
				print "  %20s:  FAIL       %-50s    [VIEW]" % (test.name, test.result.statusMessage)
			elif test.result.status == TestResult.StatusType.WARN:
				print "  %20s:  WARN       %-50s    [VIEW]" % (test.name, test.result.statusMessage)
			elif test.result.status == TestResult.StatusType.NA:
				# skip any that aren't relevant for this vehicle/hardware/etc
				continue
			else:
				print "  %20s:  UNKNOWN    %-50s" % (test.name, test.result.statusMessage)
			if test.result.extraFeedback:
				for line in test.result.extraFeedback.strip().split('\n'):
					print "  %20s     %s" % ("",line)
		print '\n'


		# temp - test some spot values
		#print "GPS abs alt on line 24126 is " + `self.logdata.channels["GPS"]["Alt"].dictData[24126]`   # 52.03
		#print "ATT pitch on line 22153 is " + `self.logdata.channels["ATT"]["Pitch"].dictData[22153]`   # -7.03
		#gpsAlt = self.logdata.channels["GPS"]["Alt"]
		#print "All GPS Alt data: %s\n\n" % gpsAlt.dictData
		#gpsAltSeg = gpsAlt.getSegment(426,711)
		#print "Segment of GPS Alt data from %d to %d: %s\n\n" % (426,711,gpsAltSeg.dictData)

	def outputXML(self, xmlFile):
		# TODO: implement XML output
		# ...
		raise Exception("outputXML() not implemented yet")


def main():
	dirName = os.path.dirname(os.path.abspath(__file__))

	# deal with command line arguments
	parser = argparse.ArgumentParser(description='Analyze an APM Dataflash log for known issues')
	parser.add_argument('logfile', type=argparse.FileType('r'), help='path to Dataflash log file')
	parser.add_argument('-q', '--quiet', metavar='', action='store_const', const=True, help='quiet mode, do not print results')
	parser.add_argument('-x', '--xml', type=str, metavar='XML file', nargs='?', const='', default='', help='write output to specified XML file')
	args = parser.parse_args()

	# log the log and run the tests
	logdata = DataflashLog.DataflashLog(args.logfile.name)
	testSuite = TestSuite()
	testSuite.run(logdata)

	# deal with output
	if not args.quiet:
		testSuite.outputPlainText()
	if args.xml:
		testSuite.outputXML(args.xml)
		if not args.quiet:
			print "XML output written to file: %s\n" % args.xml


if __name__ == "__main__":
	main()

