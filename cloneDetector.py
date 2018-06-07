
#################################################################################
###################CODE CLONE VALIDATION STARTS##################################
#################################################################################


import pickle
import pybrain
import uuid
import subprocess
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


#load the trained Neural Net
fileObject = open('trainedNetwork', 'rb')
loaded_fnn = pickle.load(fileObject)




def execTxl(txlFilePath, sourceCode, lang, saveOutputFile=False):
	#get an unique file name for storing the code temporarily
	fileName = str(uuid.uuid4())
	sourceFile = 'tmp_file_dir/'+fileName+'.txt'

	
	#write submitted source code to corresponding files
	with open(sourceFile,"w") as fo:
		fo.write(sourceCode)

	#get the required txl file for feature extraction
	#txlPath = '/home/ubuntu/Webpage/txl_features/txl_features/java/PrettyPrint.txl'

	#do the feature extraction by txl
	p = subprocess.Popen(['/usr/local/bin/txl', '-Dapply', txlFilePath, sourceFile],  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()


	#convert to utf-8 format for easier readibility
	out = str(out)
	err = str(err)

	err = err.replace(sourceFile, 'YOUR_SOURCE_FILE')
	err = err.replace(txlFilePath, 'REQUIRED_TXL_FILE')

	#once done remove the temp file
	os.remove(sourceFile)


	if saveOutputFile==False:
		#print out
		return out, err
	else:
		outputFileLocation = str(uuid.uuid4())
		outputFileLocation = 'tmp_file_dir/'+outputFileLocation+'.txt'
		with open(outputFileLocation,"w") as fo:
			fo.write(out)

		return outputFileLocation, out, err
	








def getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath):
	saveOutputFile=True
	outputFileLocation1, out1, err1 = execTxl(txlFilePath, sourceCode1, lang, saveOutputFile)
	outputFileLocation2, out2, err2 = execTxl(txlFilePath, sourceCode2, lang, saveOutputFile)

	p = subprocess.Popen(['/usr/bin/java', '-jar', 'feature_extractor/calculateCloneSimilarity.jar',outputFileLocation1, outputFileLocation2],  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	similarityValue, err = p.communicate()

	
	similarityValue = str(similarityValue)
	similarityValue = similarityValue.replace('\n', '')
	err = str(err)

	#once done remove the temp files
	os.remove(outputFileLocation1)
	os.remove(outputFileLocation2)

	#print similarityValue
	
	return similarityValue




def similaritiesNormalizedByLine(sourceCode1, sourceCode2, lang):

	txlFilePath = 'txl_features/java/PrettyPrint.txl'
	type1sim_by_line = getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath)

	txlFilePath = 'txl_features/java/normalizeLiteralsToDefault.txl'
	type2sim_by_line = getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath)

	txlFilePath = 'txl_features/java/normalizeLiteralsToZero.txl'
	type3sim_by_line = getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath)

	

	return type1sim_by_line, type2sim_by_line, type3sim_by_line




def similaritiesNormalizedByToken(sourceCode1, sourceCode2, lang):

	txlFilePath = 'txl_features/java/consistentRenameIdentifiers.txl'
	type1sim_by_token = getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath)

	txlFilePath = 'txl_features/java/normalizeLiteralsToZero.txl'
	type2sim_by_token = getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath)

	txlFilePath = 'txl_features/java/normalizeLiteralsToZero.txl'
	type3sim_by_token = getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath)

	

	return type1sim_by_token, type2sim_by_token, type3sim_by_token
	











def getValidationScore(sourceCode1, sourceCode2, lang):

	type1sim_by_line, type2sim_by_line, type3sim_by_line = similaritiesNormalizedByLine(sourceCode1, sourceCode2, lang)
	#print type1sim_by_line, type2sim_by_line, type3sim_by_line

	type1sim_by_token, type2sim_by_token, type3sim_by_token = similaritiesNormalizedByToken(sourceCode1, sourceCode2, lang)
	#print type1sim_by_token, type2sim_by_token, type3sim_by_token

	network_prediction = loaded_fnn.activate([type2sim_by_line, type2sim_by_line, type3sim_by_line, type1sim_by_token, type2sim_by_token, type3sim_by_token])

	#print 'true_clone_probability_score ==> ', network_prediction[1]
	#print 'false_clone_probability_score ==> ', network_prediction[0]
	
	#return true probability score
	return 	network_prediction[1]










#Clone Detector Calling

sourceCode1 = '''
protected DrawingView createDrawingView () {
    DrawingView createdDrawingView = createDrawingView (createDrawing ());
    createdDrawingView.drawing ().setTitle (getDefaultDrawingTitle ());
    return createdDrawingView;
}
'''

sourceCode2 = '''
public Tool getDefaultTool () {
    if (fDefaultToolButton != null) {
        return fDefaultToolButton.tool ();
    } else {
        return null;
    }
}
'''

lang = 'java'

#getValidationScore(sourceCode1, sourceCode2, lang)
#execTxl('txl_features/java/PrettyPrint.txl', sourceCode1, lang)
#getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, 'txl_features/java/PrettyPrint.txl')
#similaritiesNormalizedByToken(sourceCode1, sourceCode2, lang)
#getValidationScore(sourceCode1, sourceCode2, lang)






###############
### parsing and iterating over the potential clones
###############

# tree1 = ET.parse('jHotDraw2.xml')
# root1 = tree1.getroot()
#
# tree2 = ET.parse('jHotDraw2.xml')
# root2 = tree2.getroot()



# for child1 in root1:
# 	src1 = child1.text
# 	for child2 in root2:
# 		src2 = child2.text
# 		if child1.attrib != child2.attrib:
# 			trueCloneProb = getValidationScore(src1, src2, 'java')
# 			#print trueCloneProb
# 			if trueCloneProb > 0.5:
# 				print '***************************** CLONE PAIR ***************************'
# 				print src1
# 				print ' =========================== '
# 				print src2

#
# minLine = 6
# maxLine = 10000
#
#

# for i in range(0, len(root1)):
# 	src1 = root1[i].text
# 	for j in range(i+1, len(root1)):
# 		src2 = root1[j].text
# 		trueCloneProb = getValidationScore(src1, src2, 'java')
# 		#print trueCloneProb
# 		if trueCloneProb > 0.5:
# 			print '***************************** CLONE PAIR ***************************', trueCloneProb
# 			print src1
# 			print ' =========================== '
# 			print src2


potential_clones = 'jHotDraw2.xml'
minLine = 11
maxLine = 2500
threshold = 0.5





soup = ''
with open(potential_clones) as fp:
	soup = BeautifulSoup(fp, 'lxml')

all_potential_clones = soup.find_all('source')

total_pcs = len(all_potential_clones)
#print l
number_of_clones_found = 0
print "Detecting Clones..."
for i in range(0, total_pcs):
	src1 = all_potential_clones[i].text
	src1_lines = src1.count('\n')
	#print "Progress ", i*100/l , "%"
	for j in range(i+1, total_pcs):
		src2 = all_potential_clones[j].text
		src2_lines = src2.count('\n')



		if (src1_lines >= minLine or src2_lines >= minLine) and (src1_lines <= maxLine or src2_lines <= maxLine):
			if min(src1_lines, src2_lines)*2 >= max(src1_lines, src2_lines):
				#print "HERE ", src1
				#print " src1 => ", src1_lines, " src2 => ", src2_lines
				# #print "src1 => ", src1.count('\n'), " src2 => ", src2.count('\n'), " min=> ", min(src1.count('\n'), src2.count('\n'))
				trueCloneProb = getValidationScore(src1, src2, 'java')
				#print '++++++++++++++++++++++++++++++++++++++'
				#print src1
				#print src2
				#print trueCloneProb
				#print '++++++++++++++++++++++++++++++++++++++'
				#print trueCloneProb
				if trueCloneProb > threshold:
					number_of_clones_found = number_of_clones_found + 1

					with open(potential_clones+".clones", "a") as fo:
						#fo.write(out)
						fo.write( '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
						fo.write( '0\n' )
						fo.write( '0\n' )
						fo.write( all_potential_clones[i].attrs['file'] + " " + all_potential_clones[i].attrs['startline'] + " " + all_potential_clones[i].attrs['endline'] + "\n")
						fo.write( all_potential_clones[j].attrs['file'] +  " " + all_potential_clones[j].attrs['startline'] + " " + all_potential_clones[j].attrs['endline'] + "\n")

						fo.write( '----------------------------------------\n')
						fo.write( src1 +"\n")
						fo.write( '----------------------------------------\n')
						fo.write( src2 +"\n")
						fo.write( '----------------------------------------\n')


	print "Progress : ", str(i * 100 / total_pcs), "%"


#Writting Clone Analysis Information
with open(potential_clones + ".clones", "a") as fo:
	fo.write("\n\n****************************************************\n")
	fo.write("*************Clone Analysis Stats ******************\n")
	fo.write("****************************************************\n")

	fo.write('Total Potential Clones ==> ' + str(total_pcs)+'\n')
	fo.write('Minimum Line ==> ' + str(minLine) + '\n')
	fo.write('Maximum Line ==> ' + str(maxLine) + '\n')
	fo.write('Threshold ==> ' + str(threshold) + '\n')
	fo.write('Clones Found ==> ' + str(number_of_clones_found) + '\n')

	fo.write("****************************************************\n")



print "Done"


					# print '***************************** CLONE PAIR ***************************', trueCloneProb
					# print src1
					# print ' =========================== '
					# print src2

#print "Total Clones Found:: ", c

#################################################################################
####################CODE CLONE VALIDATION ENDS###################################
#################################################################################


