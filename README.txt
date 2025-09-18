# Health Monitor

Abstract: Using resting/min/max hr data and sleep data to warn users of excessive fatigue and elevated risk of sickness. The user would input the desired values to a website, which would be sent to the model in the backend. 

Dependencies: Please install all libraries listed in requirements.txt

How to run: 
1. Download all files as is
2. Create a conda environment, and install all Dependencies
3. Open app.py in Visual Studios Code, and run the code (alternatively, you would run app.py in the conda terminal).
4. Copy the link to webpage generated in the terminal of VSCode. Run that in a browser, and test out functionality. 

Outputs to expect:
You should expect a webpage allowing you to enter your heart rate and sleep data. Once you hit 4 weeks, you'll also see a trends graph for sleep and hr. 

Limitations/Terms and Conditions:
1. Not Medical Advice
The data and insights provided by this health monitoring tool are for informational purposes only and should not be construed as medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical concerns.

2. Accuracy of Data
While the developer strives to provide accurate heart rate and anomaly detection, the system relies on algorithmic calculations and may produce false positives or negatives. Do not solely rely on this tool for health decisions (although always take good care of yourself).

3. No Liability
The developer is not responsible for any actions taken based on the data presented. Use the results of the application cautiously.

4. Data Privacy
User health data may be processed for analytical purposes, but will be handled in accordance with applicable privacy laws, as the product is meant to run locally. However, no system is completely secure, and users should be aware of potential risks.

By using this application, you acknowledge and accept these terms and limitations.

In addition to the disclaimers, the product would ideally be integrated with watch API's so that the data could be fed continuously. That is not possible due to licensing fees and timing, and, therefore, the alternative method of manual input was chosen. 

