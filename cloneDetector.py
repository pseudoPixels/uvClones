
#################################################################################
###################CODE CLONE VALIDATION STARTS##################################
#################################################################################


import pickle
import pybrain
import uuid
import subprocess
import os





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

	#out = {'type_1_similarity_by_line':type1sim_by_line, 'type_2_similarity_by_line':type2sim_by_line,'type_3_similarity_by_line':type3sim_by_line}

	return type1sim_by_line, type2sim_by_line, type3sim_by_line

	#print 'type_1_similarity_by_line', type1sim_by_line

	#return jsonify({'error_msg': 'None', 'log_msg': 'Preprocessing Source Codes...\nNormalizing Source Codes...\nCalculating Similarities...\nDone.','output': out})




def similaritiesNormalizedByToken(sourceCode1, sourceCode2, lang):

	txlFilePath = 'txl_features/java/consistentRenameIdentifiers.txl'
	type1sim_by_token = getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath)

	txlFilePath = 'txl_features/java/normalizeLiteralsToZero.txl'
	type2sim_by_token = getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath)

	txlFilePath = 'txl_features/java/normalizeLiteralsToZero.txl'
	type3sim_by_token = getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, txlFilePath)

	#out = {'type_1_similarity_by_token':type1sim_by_token, 'type_2_similarity_by_token':type2sim_by_token,'type_3_similarity_by_token':type3sim_by_token}

	return type1sim_by_token, type2sim_by_token, type3sim_by_token
	#return jsonify({'error_msg': 'None', 'log_msg': 'Preprocessing Source Codes...\nNormalizing Source Codes...\nCalculating Similarities...\nDone.','output': out})











def getValidationScore(sourceCode1, sourceCode2, lang):

	type1sim_by_line, type2sim_by_line, type3sim_by_line = similaritiesNormalizedByLine(sourceCode1, sourceCode2, lang)
	type1sim_by_token, type2sim_by_token, type3sim_by_token = similaritiesNormalizedByToken(sourceCode1, sourceCode2, lang)

	network_prediction = loaded_fnn.activate([type1sim_by_line, type2sim_by_line, type3sim_by_line, type1sim_by_token, type2sim_by_token, type3sim_by_token])

	print 'true_clone_probability_score ==> ', network_prediction[1]
	print 'false_clone_probability_score ==> ', network_prediction[0]





























#Clone Detector Calling

sourceCode1 = '''
/**
 * A class to provide a simple list of integers.
 * List resizes automatically. Used to illustrate 
 * various design and implementation details of 
 * a class in Java.
 * 
 * Version 1 only contains the instance variables and
 * the constructors
 * @author scottm
 *
 */
public class IntListVer1 {
    // class constant for default size
    private static final int DEFAULT_CAP = 10;
    
    //instance variables
    private int[] iValues;
    private int iSize;
    
    /**
     * Default constructor. Creates an empty list.
     */
    public IntListVer1(){
        //redirect to single int constructor
        this(DEFAULT_CAP);
        //other statments could go here.
    }
	public static void main(String[] args)
	{	final int NUM_FACTS = 100;
		for(int i = 0; i < NUM_FACTS; i++)
			System.out.println( i + "! is " + factorial(i));
	}
	
	public static int factorial(int n)
	{	int result = 1;
		for(int i = 2; i <= n; i++)
			result *= i;
		return result;
	}
    /**
     * Constructor to allow user of class to specify 
     * initial capacity in case they intend to add a lot
     * of elements to new list. Creates an empty list.
     * @param initialCap > 0
     */    
    public IntListVer1(int initialCap) {
        assert initialCap > 0 : "Violation of precondition. IntListVer1(int initialCap):"
            + "initialCap must be greater than 0. Value of initialCap: " + initialCap;
        iValues = new int[initialCap];
        iSize = 0;
    }
}
'''

sourceCode2 = '''
public class Factorial
{
	public static void main(String[] args)
	{	final int NUM_FACTS = 100;
		for(int i = 0; i < NUM_FACTS; i++)
			System.out.println( i + "! is " + factorial(i));
	}
	
	public static int factorial(int n)
	{	int result = 1;
		for(int i = 2; i <= n; i++)
			result *= i;
		return result;
	}
}
'''

lang = 'java'

#getValidationScore(sourceCode1, sourceCode2, lang)





#execTxl('txl_features/java/PrettyPrint.txl', sourceCode1, lang)



#getCodeCloneSimilarity(sourceCode1, sourceCode2, lang, 'txl_features/java/PrettyPrint.txl')



#similaritiesNormalizedByToken(sourceCode1, sourceCode2, lang)


getValidationScore(sourceCode1, sourceCode2, lang)


#################################################################################
####################CODE CLONE VALIDATION ENDS###################################
#################################################################################


