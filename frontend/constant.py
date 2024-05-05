map_template = """The following is a set of documents
{docs}
Given a text consisting of Reporting's potential fraud committed,  generate a chronological sequence of summaries by dividing the text into coherent chunks. Each chunk should represent a distinct event or action taken during the exchange between the bank representatives.

Maintain all relevant information and Add it below events Heading should only be in Bold related to Fraud Type Names of people involved in conversation,  Case ID, Customer id, Customer name, Account no, Transactions IDs, Card Number, Transaction ID, Recipient ID, Recipients name, Transaction Amount, Date of Transaction, Type of Purchase, Merchant Name, Payment location, Payment location,Loan Case ID, Loan Amount Applied For, Date of Loan Application,

Loan Applied Location, Cheque Number and names of the system used in the conversation. do not duplicate details if given in one event already.

Ensure that chunks are correlated with each other, following a chronological order, and providing answers or contradictions. You can use the bullet points to describe the events.

Make sure to Include "Is it a fraud or reported by mistake" Customers behaviours like  Change in spending habits Transactions amount max and min based on your understanding at the end.

inculde all the actions taken till date on the matters that are came to light.

Only show the most important cause and do not include all relevant details. keep the entire summary concise but use separation for presentation. give brief title for each event. make sure that any time or duration mentioned is included in the summary. also show the event title in bold letters. Try to identify the patterns of fraud committed based on conversation, Examine the information in the emails to determine the duration between the initiation and resolution of the complaint.

email summary can be describe using below format

<p><b> email title timestamp</b>

    <li>descr 1</li>

    <li>descr 2</li>

    <li>descr 3</li>

after all events are described, you should give the below information.

        <b>People/Parties involved in the fraud</b>

        <b>Type of fraud commited</b>

In case no inforamation found for the points ignore the field


"""

# Reduce
reduce_template = """The following is set of summaries:
{docs}
Please Ignore previous context.Take these and distill it into a final, consolidated summary of the all the email summries. 
Please do not add any new made up eamils and make sure number of summrires is equal to number of emails docs at input.
make sure email summaries is equal to input documnt emails
each email summary can be describe using below format
<p><b>email title [timestamp]</b>
<li>descr 1 </li>
<li>descr 2</li>
<li>descr 3</li>
after all events are described, you should give the below information.
<b>People/Parties involved in the fraud</b>
<b>Type of fraud commited</b>
In case no inforamation found for the points ignore the field
"""


fraud_resolution="""
Based on the provided summary,
{summary}
 please provide the optimal course of action for a bank representative to take regarding the fraud case involving customer. 
Ensure the solution is concise and focuses solely on the events described above. 
Additionally, include preventive measures for both the customer and the bank to prevent similar incidents in the future, with 5 key points. Avoid repetition and ensure each point is unique for every new fraud scenario.
"""