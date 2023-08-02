@echo off
TITLE Arch Robot
:: Enables virtual env mode and then starts ArchRobot
env\scripts\activate.bat && py -m ArchRobot
