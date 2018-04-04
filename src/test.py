#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
re.UNICODE
from argparse import ArgumentParser 
import sys
import os
import pickle
import math
import email
import zipfile


def main():

	parser = ArgumentParser()
	parser.add_argument('emails', nargs='+', help="Emails to be tested, at least 1 is required" )
	args = parser.parse_args()

	pickleMissing = False
	
	#checks for required files
	try:
		archive1 = zipfile.ZipFile('spamData.pickle.zip', 'r')
		spamData = pickle.load(archive1.open('spamData.pickle'))
		archive2 = zipfile.ZipFile('hamData.pickle.zip', 'r')
		hamData = pickle.load(archive2.open('hamData.pickle'))
	except:
		pickleMissing = True

	
	for fileName in args.emails:

		try:
			file = open(fileName, 'r', errors='ignore')
		except IOError:
			print(fileName+' - FAIL - failed to open email file')
			continue

		if pickleMissing:
			print(fileName+" - FAIL - failed to open files: 'hamData.pickle.zip', spamData.pickle.zip")
			continue

		emailContent = getMailContent(file)
		scorer = EmailScorer(hamData, spamData, emailContent)
		result = scorer.determineEmail(); #0 = spam, 1 = ham

		if result == 1:
			print(fileName+ ' - OK')
		elif result == 0:
			print(fileName+ ' - SPAM')


def getMailContent (file):

	mail = email.message_from_file(file)
	body = mail.get_payload()

	if type(body) is list:
		body = body[0] 
	if type(body) is not str:
		body = str(body)

	subject = str(mail.get('subject'))
	validMail = subject + body
	return validMail

class EmailScorer:

	#positive values gives less false positives and more false negatives, negative value opposite
	FILTER_SENSITIVITY = 20 

	hamData = None
	spamData = None
	fileContent = None

	#take real data into account
	spamPercentage = 0.5933
	hamPercentage = 1 - spamPercentage

	#use unbiased data (50/50) 
	spamPercentagedef = 0.5
	hamPercentagedef = 0.5

	spamWordCount = 3483635
	hamWordCount = 5532691
	uniqueWordCount = 149832


	def __init__(self, hamData, spamData, fileContent):
		self.hamData = hamData
		self.spamData = spamData
		self.fileContent = fileContent

	#history data - use real spam/ham distribution to help calculate score
	def generateScore(self, spam, historyData):

		wordList = self.fileContent.lower().split()
		totalScore = 0

		if spam:
			if historyData:
				totalScore+=math.log(self.spamPercentage)
			else:
				totalScore+=math.log(self.spamPercentagedef)
		else:
			if historyData:
				totalScore+=math.log(self.hamPercentage)
			else:
				totalScore+=math.log(self.hamPercentagedef)


		for word in wordList:
			if spam:

				wordData = self.spamData.get(word, 0)
				if wordData != 0:
					totalScore += math.log(wordData)

				elif wordData == 0 and word in self.hamData:
					wordData = 1 / (self.spamWordCount + self.uniqueWordCount)
					totalScore += math.log(wordData)
				
			else:

				wordData = self.hamData.get(word, 0)
				if wordData != 0:
					totalScore += math.log(wordData)

				elif wordData == 0 and word in self.spamData:
					wordData = 1 / (self.spamWordCount + self.uniqueWordCount)
					totalScore += math.log(wordData)

		return totalScore


	def determineEmail(self):

		spamScore = self.generateScore(True, False)
		hamScore = self.generateScore(False, False)

		fullScore = hamScore - spamScore + self.FILTER_SENSITIVITY #if greater than 0 then ham...

		if (fullScore < 0):
			#print("SPAM")
			return 0
		else:
			#print("HAM")
			return 1


if __name__ == "__main__":
	main()
