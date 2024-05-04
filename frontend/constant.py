
PROMPT_USE_SHORT = """
Please provide a brief summary with respective to each email or event not more than one sentence.but use separation for presentation.

follow below instructions while generating the response:

event can be describe using below format
        <b>{event title}{timestamp}</b>
        <li>{event descr 1}</li>
        <li>{event descr 2}</li>
        <li>{event descr 3}</li>
        <b>{Root Cause of Customer Dissatisfaction}</b>
        <b>{Turn around time}{duration in number of days}</b>
"""

PROMPT_USE_LONG = """Please do not use previous request and response as context.Given a lengthy text consisting of bank customer complaints, generate a chronological sequence of events
        by dividing the text into coherent chunks. Each chunk should represent a distinct event or action taken during the exchange
        between the customer and the bank representative. Maintain all relevant information related to time, account numbers,
        and names of the system used in the conversation. Ensure that chunks are correlated with each other, following a chronological order,
        and providing answers or contradictions.you can use the bullet points to describe the events. If possible, include root cause of customer dissatisfaction based
        on your understanding at the end.only show the most important cause and do not include other irrelavent issues.
        keep the entire summary concise but use separation for presentation.
        give  brief title for each event. make sure that any time or duration mentioned is included in the summary.
        also show the event title in bold letters.Calculate the total turnaround time(days) for the customer complaint based on the provided emails or events,
        Examine the information in the emails to determine the duration between the initiation and resolution of the complaint.
        event can be describe using below format
        <p><b>{event title}{timestamp}</b>
        <li>{event descr 1}</li>
        <li>{event descr 2}</li>
        <li>{event descr 3}</li>

        after all events are described, you should give the below information.

        <b>{Root Cause of Customer Dissatisfaction}</b>
        <b>{Turn around time}{duration in number of days}</b>"""


TRANSCRIPT_SUMMARY_PROMPT = """
Please check the attached transcript. You need so identify and summarize each usecase in terms of problem statement, 
team members involved, solution approach, any challenges faced by team during usecase implementation. 
There are multiple usecase sprovided so give details for each usecase.Please give summary with enough details for each use case 
and bullet points with atleast 3-5  lines for each section if possible.
"""

