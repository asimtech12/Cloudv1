#==========================================================================================================
#  @
#  This script has the operating System specific Command which modifies jar manifest in windows paltform
#==========================================================================================================
# Imports
#==========================================================================================================
import sys
import os
import zipfile
from java.lang import System
from java.io import File
from java.io import FileOutputStream
from java.util.zip import ZipEntry
from java.util.jar import JarOutputStream
from java.util.jar import JarFile
from java.util.jar import Manifest
#=========================================================================================================
# Global Variables
#=========================================================================================================
META_INF_DIR             = "META-INF/"
MANIFEST_FILE_ENTRY      = META_INF_DIR+"MANIFEST.MF" 
JAR_EXTENSION            = ".jar"
CLASS_PATH_STR           = "Class-Path"
EXTN_NAME_STR            = "Extension-Name"
FND_SETUP_MODEL_JAR      = "FndSetupModel.jar"
FND_SETUP_FA_MODEL_JAR   = "FndSetupFAModel.jar"
FND_SETUP_UI_JAR         = "FndSetupUi.jar"
FND_SETUP_FA_UI_JAR      = "FndSetupFAView.jar"
NEW_LINE                 = "\n"
PARENT_DIR               = ".."
APPLICATIONS_DIR         = "applications"
EXPLODED_DIR             = "exploded"
FND_SETUP_EAR            = "FndSetup.ear"
APP_INF_DIR              = "APP-INF"
LIB_DIR                  = "lib"
FND_DIR                  = 'fnd'
DEPLOY_DIR               = 'deploy'
MODEL_DIR                = 'model'
ATGPF_DIR                = 'atgpf'

APPEND_CLASSPATH_ENTRY   = 0 
FLEX_MODEL_JAR_DIRS      = []
#($ADE_VIEW_ROOT/atgpf/applcore/dist/oaext/test/flex/deployment/model/)
#=========================================================================================================
#
#=========================================================================================================
def processArgs() :
	global FLEX_MODEL_JAR_DIRS
	print '===================================================================================================================================='
	print ' Usage in case FA Product Jars Staged Location to be scanned'
	print ' (By Default this script takes the Directory \'[ATGPF_ORACLE_HOME]/../applications/fnd/model/\' for Model Jars)' 
	print '===================================================================================================================================='
	print ' $JDEV_HOME/wlserver_10.3/common/bin/wlst.sh prepare_FndSetup_Jars.py <FLEX_MODEL_JAR_DIR>'
	print ' <FLEX_MODEL_JAR_DIR> is the relative path of the Staged Location of model jars ,to the directory of FndSetupModel.jar.'
	print ' Incase default directory to be scanned (\'[ATGPF_ORACLE_HOME]/../applications/fnd/model/\' for Model Jars , do not provide any arguments'
	print '===================================================================================================================================='
	print NEW_LINE
	if ( len(sys.argv) > 1 ) :
		if( not sys.argv[1] in FLEX_MODEL_JAR_DIRS ) :
			FLEX_MODEL_JAR_DIRS.append(sys.argv[1])
#=========================================================================================================
#
#=========================================================================================================
def startProcess() :
	processArgs()
	print 'Platform : '+sys.platform
	osName = System.getProperty("os.name")  
	print 'Operating System : '+osName+NEW_LINE+NEW_LINE

	currentDir = str(os.getcwd())
	jarDirectory = File(currentDir+os.sep+PARENT_DIR+os.sep+PARENT_DIR+os.sep+PARENT_DIR+os.sep+APPLICATIONS_DIR+os.sep+FND_DIR+os.sep+DEPLOY_DIR+os.sep).getCanonicalPath()
	jarFiles = File(jarDirectory).list()
	try :
		for jarFileName in jarFiles :
			if( jarFileName.endswith(FND_SETUP_MODEL_JAR) ):
				print 'Backing up FndSetupModel.jar ...'
				os.system('cp '+(jarDirectory+os.sep+FND_SETUP_MODEL_JAR)+' '+(jarDirectory+os.sep+FND_SETUP_MODEL_JAR)+'.bak')
				processJarFile(jarDirectory , FND_SETUP_MODEL_JAR , FLEX_MODEL_JAR_DIRS)
	except TypeError :
		print 'Exception : Please check the Directory :\''+jarDirectory +'\'  \nException Detail :',  sys.exc_info()[0]
#=========================================================================================================
#
#=========================================================================================================
def processJarFile( fAJarFileDir , jarFileName , relativePaths) :
	extensionIndex = jarFileName.find(JAR_EXTENSION)
	if ( extensionIndex > 0 ) : 
		extensionName = jarFileName[0 : extensionIndex ]	
	System.setProperty( "user.dir",fAJarFileDir)
	try :
	        print '   jar File: '+fAJarFileDir+os.sep+jarFileName+NEW_LINE
		jarfile = JarFile(fAJarFileDir+os.sep+jarFileName)
		manifest = jarfile.getManifest()
		attrs = manifest.getMainAttributes()
		out = JarOutputStream(FileOutputStream(fAJarFileDir+os.sep+jarFileName))
		m = Manifest();
		attrKeys = attrs.keySet()
		for attrName in  attrKeys : 
			try :
				if ( CLASS_PATH_STR == attrName.toString()  ) :
					FLEX_MODEL_JAR_MANIFEST = ''
					for relativePath in relativePaths :
					        print 'Model jar Dir: '+relativePath+NEW_LINE
						manifestStr = attrs.get(attrName)
						FLEX_MODEL_JAR_MANIFEST = getManifestForModelJars(fAJarFileDir+os.sep+relativePath,relativePath,manifestStr)		
					if( FLEX_MODEL_JAR_MANIFEST == '' ) :
						print 'No product Jar Files found to add to Manifest , exiting...'
					m.getMainAttributes().putValue( attrName.toString(), FLEX_MODEL_JAR_MANIFEST)
#					print 'Manifest Entry:\''+attrName.toString()+'\' Value :'+FLEX_MODEL_JAR_MANIFEST+'\n'
				else :
					m.getMainAttributes().putValue( attrName.toString(), attrs.get(attrName))
			except KeyError :	
				print 'Problem in getting Manifest Entries'  
		m.getMainAttributes().putValue( EXTN_NAME_STR, extensionName )
		manifestEntry = ZipEntry(MANIFEST_FILE_ENTRY)	
		out.putNextEntry(manifestEntry)
		m.write(out)
		out.closeEntry()
		e = ZipEntry(META_INF_DIR)
		out.putNextEntry(e)
		out.closeEntry()
		out.close()
	except IOError :
		print 'Problem in writing new Manifest to :\''+jarFileName +'\' \nException Detail :',  sys.exc_info()[0]
#=========================================================================================================
#
#=========================================================================================================
def getManifestForModelJars(modelJarDir, relativePath, manifestStr) :
	jarFiles = File(modelJarDir).list()
	currentDir = str(os.getcwd())
	try :
		for jarFileName in jarFiles :
			if( jarFileName.endswith(JAR_EXTENSION) ) :
				if ( manifestStr != '' ) :
					relativeJarFileName = relativePath+os.sep+jarFileName
					if (relativeJarFileName in manifestStr):
             					print '  --- skip adding jar: '+relativeJarFileName
					else :
             					print '  +++ adding jar: '+relativeJarFileName
						manifestStr = manifestStr+' '+relativePath+os.sep+jarFileName
				else :
					manifestStr = relativePath+os.sep+jarFileName
	except TypeError :
		print 'Exception : Please check the Relative path \''+relativePath +'\' is valid (Relative path between FndSetupModel.jar and model jar staged directory)\nException Detail :',   sys.exc_info()[0]
	return 	manifestStr	
#=========================================================================================================
#
#=========================================================================================================
startProcess()


