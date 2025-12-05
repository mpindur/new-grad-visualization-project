# IDS Final Project Report
## Introduction

Our project involves working with a dataset regarding employment from the CORGIS Dataset Project (https://corgis-edu.github.io/corgis/csv/graduates/). With this dataset, we plan to address the difficulty students face when trying to navigate the confusing and intimidating new grad market. We want them to be able to visualize and compare the new grad opportunities and how the landscape of the pipeline from graduation to industry has changed over the years. As students, we understand the benefit of this information being available and accessible - and will seek to present it in such a way where similar job-seeking students can extract the most value out of our interactive visualizations - making it easy and intuitive to use. We could show how many graduates in a specific field either are unemployed, end up in a job similar to the field they studied in, end up in a job different from a field they studied in, and have different reasons for unemployment or working at an outside field. 

The data in this library comes from the National Survey of Recent College Graduates, and it is accessible and downloadable straight from the hyperlinked website. This dataset includes fields such as the major and degree for graduated students, salaries, demographic information, employment status, reasons for unemployment and industry of employment, which will provide more than enough data for us to create visualizations.

Overall, we feel there is real value in this project not only to present students, but for anyone seeking to understand the larger picture of new-grad opportunities and how they have changed over time.


## Related Work

There has been a tremendous amount of research done into the job market specifically for new graduates as the economy began to recover from the pandemic and as the AI boom took place. A large part of this research deals specifically with unemployment. For example, the Federal Reserve Bank of New York made a similar visualization tool specifically detailing employment for new grads across the past 3 decades. The visualizations display unemployment, underemployment, and median wages across time. They also display career outcomes by major in a tabular form. While this is similar to the tool we are creating, one flaw in this research we hope to address is the lack of depth in diving into specific major outcomes as well as demographics for new grads. 

Another piece of similar research was done by the Federal Reserve Bank of Cleveland. This research did not focus on major outcomes or act solely as a visualization tool, rather walking readers through different data surrounding unemployment entry and exit rates and finding that it has become harder for new grads recently to find jobs, with discouragement steadily rising.

Finally, research done by the National Association of Colleges and Employers found that overall the number of mean job offers new grads are receiving have declined since the beginning of the decade. 

Essentially, these 3 pieces of research present a small sample of work done into the matter of employment when it comes specifically to new college graduates. These 3 pieces of research further paint a similar picture: that employment has become more difficult for college graduates, and college graduates are feeling this difficulty, becoming more and more pessimistic about outcomes. We hope that our tool will help students in this regard and allow them to make more confident and informed decisions about pursuing a career. We also hope that our tool differentiates from the research already done into this topic by focusing on major-specific outcomes rather than general unemployment and being an interactive tool rather than a static page of graphs.


## Methods

The CORGIS Graduates dataset was mostly clean, so we didn’t need too many cleaning steps. We have run checks such as viewing the first rows, checking column types, and looking at basic statistics to make sure the data looks right and there are no hidden problems like duplicates or strange text values. There are also no null values. There are some majors which have either 0 counts or unreasonably high counts across all columns. For these majors, we will likely not include them in any visualizations if that year is included. However, for many of these majors, data populates in later years. Some small conversions will help calculations, for example we will convert salary and other numeric columns to numpy numeric types, convert year fields to integers, and normalize text columns. From the data (means and standard deviations are provided) we will derive salary quartiles (25th, 50th, 75th), top-percentile cutoffs (top 5% and top 10%), and year over year salary changes. We may also compute z-scores or other normalized values to compare across majors. 

Our data processing stage used Numpy and Pandas: Pandas for reading, grouping, and aggregating, and Numpy for numeric work and percentiles when needed. We computed grouped aggregates by year and major and built a Streamlit app that lets users filter by year or major and that updates charts and tables automatically, with the backend using the Streamlit API to update visualizations. 

Our overall primary dashboard code is structured as follows:
We implement the filtering logic using pandas first, allowing users to filter by major and year and update the dataframe through these filters.
We set up the aggregations using pandas, and further make functions to consolidate all of our chart making code so that we don’t have to repeat code
Finally, we use streamlit to display the different plots using the filtered data

Overall, our code does not incorporate any complex statistical algorithms.


## Results

The visualizations that we see for our project are quite intricate and detailed. Starting from the filter options, you can select 47 different majors, and you can filter the data from years 1993 to 2015. Our visualizations will then display the median salary of all the people who are contained in the filter - including details like ethnicity, gender, and degree type (Bachelor’s, Master’s, Doctorate) through multiple pie charts. You’ll also be able to view the employment statistics of all the new graduates - what percentage of people are employed, what percentage of people are unemployed, and what percentage are not in the labor force. Upon further inspection, clicking on the different slices/parts of the employment statistic donut graph will reveal more statistics. Clicking on the employment slice of the graph reveals the top 3 ‘Work Activity’ categories, as well as a bar chart below that shows the comparison of workers in different occupations compared to others. You’ll also see a smaller graph that shows the percentage of how many people are working in the field they studied in versus outside of the field they’re studying in, and another bar chart for why those people are working outside of their field. Clicking on either the ‘Not in Labor Force’ or the ‘Unemployed’ sections of the Employment graph will reveal a bar graph showing the distribution of unemployed people based on their reasons for unemployment, which include ‘No need/want’, ‘Family’, ‘No Job Available’, ‘Student’, or ‘Layoff’.

We believe the details and statistics shown in our visualizations help solve the problem for new graduates. Being able to view the reasons for unemployment for the people who graduated from the same major/field can allow students to figure out what their next steps should be, and being able to view what percentage of people in their field are employed in a job in the same field is a good indicator of how likely they are to land a job. Additionally, viewing these statistics as even a high school student applying to college may allow them to make a more informed decision on what major to pursue, if their goal is to land a job easily, a job based on median salary, etc.


## Discussion

Our project shows how employment data can be made easier to understand for students who are looking for jobs after graduation. The interactive visualizations we created let users see information that would be hard to find just by looking at the raw data.

Furthermore, our system shows how employment outcomes are different across majors and years. With 47 majors to choose from and data from 1993 to 2015, students can see how job trends and employment have changed over time. For example, they can see how certain fields became more competitive, or how salaries changed. This helps students understand that the job market today is connected to what happened in the past.

Next, the demographic breakdowns in our pie charts let students see how outcomes differ based on ethnicity, gender, and degree level. This helps students know what to expect and see where there might be challenges or opportunities. The salary visualizations make it easy to compare pay across different groups and degree types, which is information that's usually hard to find in one place.

Additionally, our visualization goes beyond just showing who has a job and who doesn't. When you click on the donut chart, you can see what types of work people do, what jobs they have, and whether they work in their field or not. The data on why people work outside their field shows that many graduates end up in different careers than they planned, and that it is actually quite common.

Finally, an extra important thing our system does is explain why people are unemployed. Students using it can see that unemployment is not always because there are no jobs. For example, many graduates go back to school, or take care of family, or just don't need to work right away. This information can help students worry less about finding a job immediately after graduation.

As students ourselves, we strongly believe users (intended as other students) will like being able to compare their major to others and see real numbers instead of just hearing opinions. The interactive features will make them want to explore more, and we hope they will look at majors they were not studying to get a better sense of the overall job market. The system then will do exactly what we want it to do, to make employment data easy to use and understand.


## Future Work

There are several ways we could improve and expand our system to make it more useful for students.

First, we could add more recent data. Our dataset only goes up to 2015, but a lot has changed since then. Adding data from 2016 to 2025 would make the system more relevant to students today. We could also add current job posting data to show what jobs are available right now for different majors.

Second, we could add features that predict future trends. Using machine learning, we could show students which fields might become more or less competitive in the future. We could also build a recommendation system that suggests related majors or career paths based on what a student is interested in.

Third, we could add location data. Students need to decide where to live after graduation, so it would help to see how salaries and job opportunities differ by city or state. We could add maps that show where jobs are concentrated for different majors.

Fourth, we could make it easier to compare multiple majors at once. Right now you can only look at one major at a time, but it would be useful to see side-by-side comparisons of salary, employment rates, and other information for several majors. We could also let users save and export reports based on what they selected.

Fifth, we could bring in more types of data. For example, we could add information about student loan debt to show the financial cost of different degrees. We could also include job satisfaction data to show which fields make people happier. Adding information about career growth over time would help students think beyond just their first job.

Finally, we could add personalized features. Users could create accounts to save what they are interested in, bookmark things they find useful, and get updates when new data comes out for their major. We could also add guides that explain how to read the visualizations and use the data to make decisions.

These changes would make our system a more complete resource for students planning their careers.







