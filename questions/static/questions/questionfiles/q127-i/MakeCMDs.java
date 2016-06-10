//import java.util.Scanner;
import java.io.*;

public class MakeCMDs {
	static String div = "/";

	static String scriptsLocation = "java -cp /u2/jgorzny/scripts/gsoc14";

	public static void main(String[] args)  {

		//location of the CSV file outlining experiments
		boolean makeE = false;
        boolean makeConverted = true;
		String configFile = "";
		if(!makeE && !makeConverted){
			configFile = "/home/jgorzny/scripts/gsoc14/configs/SPASS.csv";
		} else {
			configFile = "/home/jgorzny/scripts/gsoc14/configs/E.csv";
		}
        
        if(makeConverted && !makeE){
            configFile = "/home/jgorzny/scripts/gsoc14/configs/SPASS-smt.csv";
        } else if (makeConverted && makeE){
            configFile = "/home/jgorzny/scripts/gsoc14/configs/E-smt.csv";
        }

		//Folder to output scripts generated. should not end with a slash
		String scriptOutDir = "";
        if(makeConverted){
            scriptOutDir = "/home/jgorzny/scripts/gsoc14/configs/smtdata";
        }else {
            scriptOutDir = "/home/jgorzny/scripts/gsoc14/configs";
        }

		//Where are the files stored ON THE SYSTEM THE EXPERIMENT WILL EXECUTE ON
		//e.g. "..\\TPTP-v6.2.0-Oct-10-2015\\TPTP-v6.2.0\\Problems"
		String problemsDir = "/home/jgorzny/data/gsoc14/TPTP-v6.2.0-Oct-10-2015/TPTP-v6.2.0/Problems";
		String problemsDirCASC = "/home/jgorzny/data/gsoc14/CASC25-Problems-12-Oct-2015/Problems";
        String problemsDirSMTbase = "/u2/jgorzny/data/gsoc14/SMTConverterOut";
        String problemsDirSMT = "";

		//where are the data set list files stored ON THE SYSTEM THE SCRIPT WILL EXECUTE ON
		String dataSetDir = "";
        if(makeConverted){
            dataSetDir = "/home/jgorzny/scripts/gsoc14/datasets/smtconverted";
        } else {
            dataSetDir = "/home/jgorzny/scripts/gsoc14/datasets";
        }
		//where should generated data be stored ON THE SYSTEM THE EXPERIMENT WILL EXECUTE ON
		//should not end with slash
		String outputBase = "/home/jgorzny/results/gsoc14";

//		String scriptsLocation = "/u2/jgorzny/scripts/gsoc14";

		try {

			//parse the config file
			FileReader fileReader = new FileReader(configFile);
			BufferedReader bufferedReader = new BufferedReader(fileReader);

			if(!makeE){
				String header = bufferedReader.readLine(); //never used
				System.out.println("CSV header: " + header);
			}

			while(bufferedReader.ready()){
				String line = bufferedReader.readLine();
				if(line.length() == 0){
					break;
				}

				System.out.println("Making script for " + line);

//				Scanner lineScanner = new Scanner(line);
//				lineScanner.useDelimiter(",");
//				String expName =  lineScanner.next();
//				String description = lineScanner.next();
//				String flags = lineScanner.next();
//				String problemSet = lineScanner.next();

				//See http://stackoverflow.com/questions/1757065/java-splitting-a-comma-separated-string-but-ignoring-commas-in-quotes
		        String[] tokens = line.split(",(?=([^\"]*\"[^\"]*\")*[^\"]*$)", -1);
				String expName =  tokens[0];
				String description = tokens[1];
				String flags = tokens[2];
				String problemSet = tokens[3];



				try {

					boolean isCASC = false;
                    int isSMTdata = -1;
					String tptpListFile = "";
					if (problemSet.equals("TPTP-FO")) {
						tptpListFile = "tptp-RealFONoEq-list.txt";
					} else if (problemSet.equals("TPTP-HU")) {
						tptpListFile = "tptp-FiniteHUNoEq-list.txt";
					} else if (problemSet.equals("TPTP-AP")) {
						tptpListFile = "tptp-'Propositional'NoEq-list.txt";
					} else if (problemSet.equals("TPTP-P")) {
						tptpListFile = "tptp-PropositionalNoEq-list.txt";
					} else if (problemSet.equals("TPTP-All")) {
						tptpListFile = "tptp-allNoEq-list.txt";
					} else if (problemSet.equals("CASC25")) {
						isCASC=true;
						tptpListFile = "casc-all.txt";
                    } else if(problemSet.equals("SMTout0")){
                        isSMTdata = 0;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout1")){
                        isSMTdata = 1;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout2")){
                        isSMTdata = 2;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout3")){
                        isSMTdata = 3;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout4")){
                        isSMTdata = 4;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout5")){
                        isSMTdata = 5;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout6")){
                        isSMTdata = 6;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout7")){
                        isSMTdata = 7;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout8")){
                        isSMTdata = 8;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout9")){
                        isSMTdata = 9;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout10")){
                        isSMTdata = 10;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout11")){
                        isSMTdata = 11;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout12")){
                        isSMTdata = 12;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout13")){
                        isSMTdata = 13;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout14")){
                        isSMTdata = 14;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout15")){
                        isSMTdata = 15;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                       tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout16")){
                        isSMTdata = 16;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout17")){
                        isSMTdata = 17;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout18")){
                        isSMTdata = 18;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";
                    } else if(problemSet.equals("SMTout19")){
                        isSMTdata = 19;
                        problemsDirSMT = problemsDirSMTbase + "/" + isSMTdata;
                        tptpListFile =  "\"" + problemsDirSMTbase + "/" + isSMTdata + "/logs/good.txt\"";                       
                        
					} else {
//						lineScanner.close();
						throw new Exception ("Data set not found: " + problemSet);
					}

					String processedTPTPlist = "\"" + dataSetDir + div + "processed" + div + expName + "-processed-" + tptpListFile + "\"";

					String outputFolder = outputBase + div + expName + div;
					String statsFileName = outputFolder + "logs" + div + "stats.txt";
					String errorFileName = outputFolder + "logs" + div + "errors.txt";

					String outputExtension = "";
					if(!makeE){
						outputExtension="spass";
					}else{
						outputExtension="eproof";
					}

					String newListName = outputFolder + "logs" + div + "newList.txt";
					String collectedDir = outputFolder + "succesful" + div;
					String stepOne = "";
					if(isCASC){
						stepOne = makeProcessTPTPlist(expName, dataSetDir, problemsDirCASC, problemSet, tptpListFile, processedTPTPlist);
                    } else if(isSMTdata > -1){
                        stepOne = ""; //Do nothing - we don't make a processed list for this
					} else {
              			stepOne = makeProcessTPTPlist(expName, dataSetDir, problemsDir, problemSet, tptpListFile, processedTPTPlist);
					}
					String stepTwo = "";
					if(isCASC){
						stepTwo = makeRunExperiment(expName, processedTPTPlist, problemsDirCASC,
							outputFolder, statsFileName, errorFileName, flags, outputExtension, makeE);
                    } else if(isSMTdata > -1){
                        stepTwo = makeRunExperiment(expName, tptpListFile, problemsDirSMT,
							outputFolder, statsFileName, errorFileName, flags, outputExtension, makeE);
				    } else {
						stepTwo = makeRunExperiment(expName, processedTPTPlist, problemsDir,
							outputFolder, statsFileName, errorFileName, flags, outputExtension, makeE);
				    }
					String stepThree = "";
                    if(isSMTdata > -1){
                        stepThree =  makeGetFilteredSMT(tptpListFile, errorFileName, newListName);
                    } else {
                        stepThree = makeGetFiltered(processedTPTPlist, errorFileName, newListName);
                    }
					String stepFour = makeCollect(newListName, collectedDir, outputFolder, outputExtension);

					File expScript = new File(scriptOutDir + div + expName + ".txt" );
					PrintWriter scriptWriter = new PrintWriter(expScript, "UTF-8");
					scriptWriter.println("#!/bin/bash");
					scriptWriter.println("# Experiment name: " + expName);
					scriptWriter.println("# Description: " + description);
					scriptWriter.println("\n\n");
					scriptWriter.println(stepOne);
					scriptWriter.println(stepTwo);
					scriptWriter.println(stepThree);
					scriptWriter.println(stepFour);
					scriptWriter.close();

				} catch (Exception e) {
					System.err.println("Could not make script for experiment " + expName);
					e.printStackTrace();
				}

//				lineScanner.close();

			}
			bufferedReader.close();

		} catch (Exception e) {
			System.err.println("Error!");
			e.printStackTrace();
		}
	}

	private static String makeProcessTPTPlist(String expName, String dataSetDir,
			String problemsDir, String problemSet, String tptpListFile, String processedTPTPlist) throws Exception {

		String tptpListFileWithDir = "\"" + dataSetDir + div + tptpListFile + "\"";
		String tptpProblemsDirectory = "\"" + problemsDir	+ "\"";
		return scriptsLocation+div+" ProcessTPTPList " + tptpListFileWithDir + " " +
		processedTPTPlist + " " + tptpProblemsDirectory;
	}

	private static String makeRunExperiment(String expName, String processedTPTPList,
			String tptpProblemsDirectory, String outputFolder, String statsFileName, String errorLogName,
			String flags, String outputExtension, boolean makeE) {

		String executable = "";
		if(!makeE){
			executable = "/u2/jgorzny/bin/SPASS-3.7/SPASS/SPASS";
		} else {
			executable = "/u2/jgorzny/bin/E/PROVER/eprover";
		}
		String executableNameShort = "";
		if(!makeE){
			executableNameShort = "SPASS";
		} else {
			executableNameShort = "E";
		}


		return scriptsLocation+div+" RunExperiment " + "\"" + expName + "\" " +
		processedTPTPList + " \"0\" " +
		"\"" + tptpProblemsDirectory + "\" " +
		"\"" + outputFolder + "\" " +  "\"" + statsFileName + "\" "+
		"\"" + executable + "\" " +"\"" + flags + "\" " +
		"\"" + errorLogName + "\" " + "\"" + outputExtension + "\" " +
		"\"" + executableNameShort + "\"";
	}

	private static String makeGetFiltered(String processedTPTPList, String errorLogName, String newListName) {
		return scriptsLocation+div+" GetFilteredList " + processedTPTPList + " " +
				"\"" + errorLogName + "\" " + "\"" + newListName + "\"";
	}
	private static String makeGetFilteredSMT(String processedTPTPList, String errorLogName, String newListName) {
		return scriptsLocation+div+" GetFilteredList " + processedTPTPList + " " +
				"\"" + errorLogName + "\" " + "\"" + newListName + "\"";
	}    

	private static String makeCollect(String newListName, String targetDir, String problemsDir, String extension) {
		return scriptsLocation+div+" CollectProofsSix " +"\"" + newListName + "\" " +
				"\"" + targetDir + "\" " + "\"" + problemsDir + "\" "  + "\"" + extension + "\"" ;
	}

}
