import pickle
import pybrain
import uuid
import subprocess
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# load the trained Neural Net
fileObject = open('trainedNetwork', 'rb')
loaded_fnn = pickle.load(fileObject)


def execTxl(txlFilePath, sourceCode, lang, saveOutputFile=False):
    # get an unique file name for storing the code temporarily
    fileName = str(uuid.uuid4())
    sourceFile = 'tmp_file_dir/' + fileName + '.txt'

    # write submitted source code to corresponding files
    with open(sourceFile, "w") as fo:
        fo.write(sourceCode)

    # get the required txl file for feature extraction
    # txlPath = '/home/ubuntu/Webpage/txl_features/txl_features/java/PrettyPrint.txl'

    # do the feature extraction by txl
    p = subprocess.Popen(['/usr/local/bin/txl', '-Dapply', txlFilePath, sourceFile], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()

    # convert to utf-8 format for easier readibility
    out = str(out)
    err = str(err)

    err = err.replace(sourceFile, 'YOUR_SOURCE_FILE')
    err = err.replace(txlFilePath, 'REQUIRED_TXL_FILE')

    # once done remove the temp file
    os.remove(sourceFile)

    if saveOutputFile == False:
        # print out
        return out, err
    else:
        outputFileLocation = str(uuid.uuid4())
        outputFileLocation = 'tmp_file_dir/' + outputFileLocation + '.txt'
        with open(outputFileLocation, "w") as fo:
            fo.write(out)

        return outputFileLocation, out, err


def getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath):
    saveOutputFile = True
    outputFileLocation1, out1, err1 = execTxl(txlFilePath, sourceCode1, lang, saveOutputFile)
    outputFileLocation2, out2, err2 = execTxl(txlFilePath, sourceCode2, lang, saveOutputFile)

    p = subprocess.Popen(
        ['/usr/bin/java', '-jar', 'feature_extractor/calculateCloneSimilarity.jar', outputFileLocation1,
         outputFileLocation2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    similarityValue, err = p.communicate()

    similarityValue = str(similarityValue)
    similarityValue = similarityValue.replace('\n', '')
    err = str(err)

    # once done remove the temp files
    os.remove(outputFileLocation1)
    os.remove(outputFileLocation2)

    # print similarityValue

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
    # print type1sim_by_line, type2sim_by_line, type3sim_by_line

    type1sim_by_token, type2sim_by_token, type3sim_by_token = similaritiesNormalizedByToken(sourceCode1, sourceCode2,
                                                                                            lang)
    # print type1sim_by_token, type2sim_by_token, type3sim_by_token

    network_prediction = loaded_fnn.activate(
        [type2sim_by_line, type2sim_by_line, type3sim_by_line, type1sim_by_token, type2sim_by_token, type3sim_by_token])

    # print 'true_clone_probability_score ==> ', network_prediction[1]
    # print 'false_clone_probability_score ==> ', network_prediction[0]

    # return true probability score
    return network_prediction[1]














lines = ''
with open('DetectedClones/ForEval/jLipSync.clones') as fp:
    lines = fp.readlines()


firstFragmentStart = False
secondFragmentStart = False

firstFragment = ''
secondFragment = ''

lineStr = ''

for aLine in range(0, len(lines)):
    lineStr += lines[aLine]

clonePairs = lineStr.split("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

for aClonePair in range(1, len(clonePairs)):
    cloneInfo = clonePairs[aClonePair]

    firstFragment = cloneInfo.split("----------------------------------------")[1]
    secondFragment = cloneInfo.split("----------------------------------------")[2]

    vs = getValidationScore(firstFragment, secondFragment, 'java')

    print (vs)


