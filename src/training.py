#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
re.UNICODE
from argparse import ArgumentParser 
import sys
import os
import pickle
import email


def main():

	trainer = Trainer()
	trainer.trainFilter()


class Trainer:

	emailCounter=0

	pathToHamC1='data/training/corpus1/ham'
	pathToSpamC1='data/training/corpus1/spam'

	pathToEmailsC2='data/training/corpus2'

	pathToHamC3='data/training/corpus3/ham'
	pathToSpamC3='data/training/corpus3/spam'

	pathToEmailsC4='data/training/corpus4'

	pathToEmailsC5='data/training/corpus5'

	pathToEmailsC6='data/training/corpus6'

	fullWordSet = set([])
	spamWordSet = set([])
	hamWordSet = set([])

	hamWordsOccCnt={}
	hamCondProb={}
	hamWordCount=0

	spamWordsOccCnt={}
	spamCondProb={}
	spamWordCount=0

	def __init__(self):
		pass

	#counts number of occurences of all words in emails
	def getFileData(self, fileName, spam):

		self.emailCounter+=1

		file = open(fileName, 'r', errors='ignore')
		emailContent = self.getMailContent(fileName).lower()
		wordList=emailContent.split()

		if spam:
			self.spamWordCount+=len(wordList)
		elif not spam:
			self.hamWordCount+=len(wordList)

		wordSet = set(wordList)

		for word in wordList: #all occurences in email
		#for word in wordSet: #max 1 occurence in email

			if word not in self.fullWordSet:
				self.fullWordSet.add(word)

			if (spam):
				if word not in self.spamWordSet:
					self.spamWordSet.add(word)

				self.spamWordsOccCnt[word] = self.spamWordsOccCnt.get(word, 0) +1
			elif (not spam):

				if word not in self.hamWordSet:
					self.hamWordSet.add(word)
				self.hamWordsOccCnt[word] = self.hamWordsOccCnt.get(word, 0) +1


	def calculateConditionalProbability(self, spam):

		uniqueWordCount = len(self.fullWordSet)

		if spam:
			for word in self.spamWordSet:
				self.spamCondProb[word]=(self.spamWordsOccCnt.get(word, 0) + 1) / (self.spamWordCount + uniqueWordCount)
		elif not spam:
			for word in self.hamWordSet:
				self.hamCondProb[word]=(self.hamWordsOccCnt.get(word, 0) + 1) / (self.hamWordCount + uniqueWordCount)	


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

	def trainCorpus1(self):

		for fileName in os.listdir(self.pathToHamC1):
			self.getFileData(self.pathToHamC1+'/'+fileName, False)

		for fileName in os.listdir(self.pathToSpamC1):
			self.getFileData(self.pathToSpamC1+'/'+fileName, True)
			#print(fileName)

	def trainCorpus2(self):

		content = open(self.pathToEmailsC2 + '/SPAMTrain.label', errors='ignore').read()
		emailDict={}
		for line in content.split("\n"):
			emailDict[line.split(' ')[1]]=int(line.split(' ')[0])

		for fileName in os.listdir(self.pathToEmailsC2+'/training'):

			if emailDict[fileName]==1:
				self.getFileData(self.pathToEmailsC2+'/training/'+fileName, False)
			elif emailDict[fileName]==0:
				self.getFileData(self.pathToEmailsC2+'/training/'+fileName, True)

	def trainCorpus3(self):

		for fileName in os.listdir(self.pathToHamC3):
			self.getFileData(self.pathToHamC3+'/'+fileName, False)

		for fileName in os.listdir(self.pathToSpamC3):
			self.getFileData(self.pathToSpamC3+'/'+fileName, True)

	def trainCorpus4(self):

		content = open(self.pathToEmailsC4 + '/index', errors='ignore').read()
		emailDict={}
		for line in content.split("\n"):
			emailDict[line.split(' ')[1][8:]]=line.split(' ')[0]

		for fileName in os.listdir(self.pathToEmailsC4+'/training'):

			if emailDict[fileName]=='ham':
				self.getFileData(self.pathToEmailsC4+'/training/'+fileName, False)
			elif emailDict[fileName]=='spam':
				self.getFileData(self.pathToEmailsC4+'/training/'+fileName, True)

	def trainCorpus5(self):

		content = open(self.pathToEmailsC5 + '/index', errors='ignore').read()
		emailDict={}
		for line in content.split("\n"):
			emailDict[line.split(' ')[1][8:]]=line.split(' ')[0]

		for root, dirs, files in os.walk(self.pathToEmailsC5+'/training'):
			for file in files:
				relDir = os.path.relpath(root, self.pathToEmailsC5+'/training')
				fileName = os.path.join(relDir, file)
				
				if emailDict[fileName]=='ham':
					self.getFileData(self.pathToEmailsC5+'/training/'+fileName, False)
				elif emailDict[fileName]=='spam':
					self.getFileData(self.pathToEmailsC5+'/training/'+fileName, True)
				

	def trainCorpus6(self):

		content = open(self.pathToEmailsC6 + '/index', errors='ignore').read()
		emailDict={}
		for line in content.split("\n"):
			emailDict[line.split(' ')[1][8:]]=line.split(' ')[0]

		for root, dirs, files in os.walk(self.pathToEmailsC6+'/training'):
			for file in files:
				relDir = os.path.relpath(root, self.pathToEmailsC6+'/training')
				fileName = os.path.join(relDir, file)
				
				if emailDict[fileName]=='ham':
					self.getFileData(self.pathToEmailsC6+'/training/'+fileName, False)
				elif emailDict[fileName]=='spam':
					self.getFileData(self.pathToEmailsC6+'/training/'+fileName, True)
				


	def trainFilter(self):

		self.trainCorpus1()
		self.trainCorpus2()
		self.trainCorpus3()
		self.trainCorpus4()
		self.trainCorpus5()
		self.trainCorpus6()

		self.calculateConditionalProbability(False)
		self.calculateConditionalProbability(True)

		with open('hamData.pickle', 'wb') as handle:
			pickle.dump(self.hamCondProb, handle, protocol=pickle.HIGHEST_PROTOCOL)

		with open('spamData.pickle', 'wb') as handle:
			pickle.dump(self.spamCondProb, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
	main()
