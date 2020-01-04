#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 23:51:23 2019

@author: Mate
"""
import os
import cryptography
import base64
from getpass import getpass
from base64 import b64encode
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

password = b""
filepath = os.path.dirname(os.path.abspath(__file__))

def getFernet(salt,pwd=""):
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt=salt,
		iterations=100000,
		backend=default_backend()
	)
	key = base64.urlsafe_b64encode(kdf.derive(password if pwd=="" else pwd))
	return Fernet(key)

def checkPassword(SecretMessage,salt):
	f = getFernet(salt)
	try:
		f.decrypt(bytes(SecretMessage))
	except cryptography.fernet.InvalidToken:
		print("Wrong Password, please try again!")
		exit()

def generateSecretMessage(salt,pwd=""):
	SecretMessage = b64encode(os.urandom(16))
	f = getFernet(salt,pwd)
	return f.encrypt(SecretMessage).decode()

def generateSalt():
	newsalt = b64encode(os.urandom(16)).decode()
	return newsalt

def decryptCSVs(salt,config):
	print("decrypting...")
	labels=["_div_trans.csv","_div.csv","_inv.csv",".csv"]
	for products in config.sections():
		name = config[products]["name"]
		for label in labels:
			if label==".csv" and config[products]["type"]!="liq": continue
			try:
				with open("csv/"+name+"/"+name+label,"rb") as file:
					data = file.read()
					print("csv/"+name+"/"+name+label,"is being decrypted...")
				decrypted = getFernet(salt).decrypt(data)
				with open("csv/"+name+"/"+name+label, 'wb') as file:
					file.write(decrypted)
			except FileNotFoundError:
				pass
	print("Done. All datasets have been decrypted in",filepath+"/csv/")

def encryptCSVs(salt,config,pwd=""):
	print("encrypting...")
	labels=["_div_trans.csv","_div.csv","_inv.csv",".csv"]
	for products in config.sections():
		name = config[products]["name"]
		for label in labels:
			if label==".csv" and config[products]["type"]!="liq": continue
			try:
				with open("csv/"+name+"/"+name+label,"rb") as file:
					data = file.read()
					print("csv/"+name+"/"+name+label,"is being encrypted...")
				encrypted = getFernet(salt,pwd).encrypt(data)
				with open("csv/"+name+"/"+name+label, 'wb') as file:
					file.write(encrypted)
			except FileNotFoundError:
				pass

def changePassword(config,settings,salt,encrypted=True):
	newpassword = getpass("Please enter your new password:\n").encode()
	if newpassword != getpass("Please confirm your new password:\n").encode():
		print("Error: The passwords did not match.")
	else:
		#generating a new salt
		newsalt = generateSalt()
		settings["settings"]["encryption_salt"] = newsalt
		newsalt = bytes(newsalt.encode())
		#generating a new secret message
		newSecretMessage = generateSecretMessage(newsalt,newpassword)
		settings["settings"]["secret_message"] = newSecretMessage
		if encrypted:
			print("Decrypting datafiles...")
			decryptCSVs(salt, config)
			print("Encrypting datafiles...")
			encryptCSVs(newsalt, config,newpassword)
		print("New Password Set.")
