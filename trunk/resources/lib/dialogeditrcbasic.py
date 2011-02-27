import xbmc, xbmcgui

import os

import util, config
from util import *

ACTION_EXIT_SCRIPT = (10,)
ACTION_CANCEL_DIALOG = ACTION_EXIT_SCRIPT + (9,)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_OK = 6000
CONTROL_BUTTON_CANCEL = 6010

CONTROL_BUTTON_EMUCMD = 5220
CONTROL_BUTTON_PARAMS = 5230
CONTROL_BUTTON_ROMPATH = 5240
CONTROL_BUTTON_FILEMASK = 5250
CONTROL_BUTTON_MEDIAPATH = 5270
CONTROL_BUTTON_MEDIAFILEMASK = 5280

CONTROL_BUTTON_IGNOREONSCAN = 5330

CONTROL_LIST_ROMCOLLECTIONS = 5210
CONTROL_BUTTON_RC_DOWN = 5211
CONTROL_BUTTON_RC_UP = 5212

CONTROL_BUTTON_MEDIA_DOWN = 5261
CONTROL_BUTTON_MEDIA_UP = 5262

CONTROL_LIST_MEDIATYPES = 5260
CONTROL_LIST_SCRAPER1 = 5290
CONTROL_LIST_SCRAPER2 = 5300
CONTROL_LIST_SCRAPER3 = 5310
CONTROL_LIST_IMAGEPLACING = 5320


class EditRCBasicDialog(xbmcgui.WindowXMLDialog):
	
	selectedControlId = 0
	selectedRomCollection = None
	
	def __init__(self, *args, **kwargs):
		Logutil.log('init Edit RC Basic', util.LOG_LEVEL_INFO)
		
		self.gui = kwargs[ "gui" ]
		
		self.doModal()
	
	
	def onInit(self):
		Logutil.log('onInit Edit RC Basic', util.LOG_LEVEL_INFO)
		
		#Rom Collections
		romCollectionList = []
		for rcId in self.gui.config.romCollections.keys():
			romCollection = self.gui.config.romCollections[rcId]
			romCollectionList.append(romCollection.name)
		self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, romCollectionList)
		
		
		self.availableScrapers = self.getAvailableScrapers()		
		self.addItemsToList(CONTROL_LIST_SCRAPER1, self.availableScrapers)
		self.addItemsToList(CONTROL_LIST_SCRAPER2, self.availableScrapers)
		self.addItemsToList(CONTROL_LIST_SCRAPER3, self.availableScrapers)
		
		self.imagePlacingList = []
		imagePlacingRows = self.gui.config.tree.findall('ImagePlacing/fileTypeFor')
		for imagePlacing in imagePlacingRows:
			self.imagePlacingList.append(imagePlacing.attrib.get('name'))
		self.addItemsToList(CONTROL_LIST_IMAGEPLACING, self.imagePlacingList)
		
		self.updateControls()
		
		
	def onAction(self, action):
		if (action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
		
	
	def onClick(self, controlID):
		if (controlID == CONTROL_BUTTON_EXIT): # Close window button
			self.close()
			
		#OK
		elif (controlID == CONTROL_BUTTON_OK):
			pass
			
		#Cancel
		elif (controlID == CONTROL_BUTTON_CANCEL):
			self.close()
			
		#Rom Collection list
		elif(self.selectedControlId in (CONTROL_BUTTON_RC_DOWN, CONTROL_BUTTON_RC_UP)):
			#HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			
			self.updateControls()
		
		#Media Path
		elif(self.selectedControlId in (CONTROL_BUTTON_MEDIA_DOWN, CONTROL_BUTTON_MEDIA_UP)):
			#HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			
			self.updateMediaPath()
	
	
	def onFocus(self, controlId):
		self.selectedControlId = controlId
	
	
	def updateControls(self):
		
		control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
		selectedRomCollectionName = str(control.getSelectedItem().getLabel())
				
		self.selectedRomCollection = None
		
		for rcId in self.gui.config.romCollections.keys():
			romCollection = self.gui.config.romCollections[rcId]
			if romCollection.name == selectedRomCollectionName:
				self.selectedRomCollection = romCollection
				break
			
		if(self.selectedRomCollection == None):
			return
		
		control = self.getControlById(CONTROL_BUTTON_EMUCMD)
		control.setLabel(self.selectedRomCollection.emulatorCmd)
		
		control = self.getControlById(CONTROL_BUTTON_PARAMS)
		control.setLabel(self.selectedRomCollection.emulatorParams)
				
		#HACK: split romPath and fileMask
		firstRomPath = ''
		fileMask = ''
		for romPath in self.selectedRomCollection.romPaths:
			
			pathParts = os.path.split(romPath)			 
			if(firstRomPath == ''):				
				firstRomPath = pathParts[0]
				fileMask = pathParts[1]
			elif(firstRomPath == pathParts[0]):
				fileMask = fileMask +',' +pathParts[1]
								
		control = self.getControlById(CONTROL_BUTTON_ROMPATH)
		control.setLabel(firstRomPath)
		
		control = self.getControlById(CONTROL_BUTTON_FILEMASK)
		control.setLabel(fileMask)
		
		
		#Media Types
		mediaTypeList = []
		firstMediaPath = ''
		firstMediaFileMask = ''
		for mediaPath in self.selectedRomCollection.mediaPaths:
			mediaTypeList.append(mediaPath.fileType.name)
			if(firstMediaPath == ''):
				pathParts = os.path.split(mediaPath.path)
				firstMediaPath = pathParts[0]
				firstMediaFileMask = pathParts[1]
				
		self.addItemsToList(CONTROL_LIST_MEDIATYPES, mediaTypeList)
		
		control = self.getControlById(CONTROL_BUTTON_MEDIAPATH)
		control.setLabel(firstMediaPath)
		
		control = self.getControlById(CONTROL_BUTTON_MEDIAFILEMASK)
		control.setLabel(firstMediaFileMask)
						
		self.selectScrapersInList(self.selectedRomCollection.scraperSites, self.availableScrapers)
		
		self.selectItemInList(self.imagePlacingList, self.selectedRomCollection.imagePlacing.name, CONTROL_LIST_IMAGEPLACING)
		
		control = self.getControlById(CONTROL_BUTTON_IGNOREONSCAN)
		control.setSelected(self.selectedRomCollection.ignoreOnScan)
	
	
	def updateMediaPath(self):
		
		control = self.getControlById(CONTROL_LIST_MEDIATYPES)
		selectedMediaType = str(control.getSelectedItem().getLabel())
		
		for mediaPath in self.selectedRomCollection.mediaPaths:
			if mediaPath.fileType.name == selectedMediaType:
				
				pathParts = os.path.split(mediaPath.path)
				control = self.getControlById(CONTROL_BUTTON_MEDIAPATH)
				control.setLabel(pathParts[0])				
				control = self.getControlById(CONTROL_BUTTON_MEDIAFILEMASK)
				control.setLabel(pathParts[1])
				
				break
	
	
	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except:
			return None
		
		return control
	
	
	def addItemsToList(self, controlId, options):
		control = self.getControlById(controlId)
		control.setVisible(1)
		control.reset()
				
		items = []
		for option in options:
			items.append(xbmcgui.ListItem(option, '', '', ''))
							
		control.addItems(items)
		
		
	def getAvailableScrapers(self):
		#Scrapers
		sitesInList = ['None']		
		#get all scrapers
		scrapers = self.gui.config.tree.findall('Scrapers/Site')
		for scraper in scrapers:
			name = scraper.attrib.get('name')
			if(name != None):
				sitesInList.append(name)
				
		return sitesInList
	
	
	def selectScrapersInList(self, sitesInRomCollection, sitesInList):
		
		if(len(sitesInRomCollection) >= 1):
			self.selectItemInList(sitesInList, sitesInRomCollection[0].name, CONTROL_LIST_SCRAPER1)			
		else:
			self.selectItemInList(sitesInList, 'None', CONTROL_LIST_SCRAPER1)
		if(len(sitesInRomCollection) >= 2):
			self.selectItemInList(sitesInList, sitesInRomCollection[1].name, CONTROL_LIST_SCRAPER2)
		else:
			self.selectItemInList(sitesInList, 'None', CONTROL_LIST_SCRAPER2)
		if(len(sitesInRomCollection) >= 3):
			self.selectItemInList(sitesInList, sitesInRomCollection[2].name, CONTROL_LIST_SCRAPER3)
		else:
			self.selectItemInList(sitesInList, 'None', CONTROL_LIST_SCRAPER3)
				
	
	def selectItemInList(self, options, itemName, controlId):				
		
		for i in range(0, len(options)):			
			option = options[i]
			if(itemName == option):
				control = self.getControlById(controlId)
				control.selectItem(i)
				break