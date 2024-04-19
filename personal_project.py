import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# Call all the necessary datasets
df = pd.read_excel("C:/Users/Hyunjin/Desktop/Personal_Project/unemployment_rate.xlsx")

# Rename the columns first to avoid confusions
new_header = list(df.iloc[0]) 
new_header[0] = "Year"
new_header[1] = "Month"
df = df[1:] 
df.columns = new_header
df = df[df['Year'].notna()]
df['Year'].iloc[-2] = 2024
df = df.reset_index()

# Change the month name to number
df = df.replace(['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June', 'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.'],
                 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])


# Convert all values in the DataFrame to numeric
df.drop(columns=df.columns[0], axis=1, inplace=True)
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
print(df["Year"])
print(df.iloc[:, 14].mean())

df = df.dropna(subset=["Year"])


# Cut the dataframe from year 2015 to 2024
df = df.loc[df['Year'] >= 2015]
# Reset the index of the dataframe
df = df.reset_index(drop=True)
df['Year'] = df['Year'].astype(int)

# Divide the dataframe into three 
lb_force = df.iloc[:, lambda df: [0, 1, 2, 3, 4]]
employee = df.iloc[:, lambda df: [0, 1, 5, 6, 7]]
employer = df.iloc[:, lambda df: [0, 1, 8, 9, 10]]
umemployed = df.iloc[:, lambda df: [0, 1, 11, 12, 13]]
unemployment_rate = df.iloc[:, lambda df: [0, 1, 14, 15, 16]]

# Draw the unemployment rate for each month for the past years
#unempl = unemployment_rate.pivot(index="Month", columns="Year", values="Both sexes")
#ax = sns.lineplot(data=unempl)
#sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
#plt.show()

unemp_by_year = unemployment_rate.groupby("Year").mean()
ax1 = sns.lineplot(data=unemp_by_year, x="Year", y="Both sexes")
ax1.set(xlabel='Year', ylabel='Unemployment Rate (%)')
#plt.savefig('C:/Users/Hyunjin/Desktop/Personal_Project/plots/Year_Unemployment.png', bbox_inches = "tight")

# Read the trend of the number of employers, employees and labour force
# Create the dataframe to draw a figure 
lb_force_by_year = lb_force.groupby("Year").mean()
lb_force_by_year = lb_force_by_year.rename(columns={"Both sexes":"Number of Labour Force"})
employer_by_year = employer.groupby("Year").mean()
employer_by_year = employer_by_year.rename(columns={"Both sexes":"Number of Employers"})
employee_by_year = employee.groupby("Year").mean()
employee_by_year = employee_by_year.rename(columns={"Both sexes":"Number of Employees"})
lb_force_employee = pd.merge(lb_force_by_year, employee_by_year, on='Year')
lb_force_employee = lb_force_employee.drop(columns=["Month_x", "Male_x", "Female_x", "Month_y", "Male_y", "Female_y"])
lb_force_employee = lb_force_employee.reset_index()
lb_force_employee = pd.merge(lb_force_employee, employer_by_year, on='Year')
lb_force_employee = lb_force_employee.drop(columns=["Month", "Male", "Female"])
lb_force_employee = lb_force_employee.reset_index()
# Draw the graph to see the trend 
ax2 = lb_force_employee.plot(x="Year", y=["Number of Labour Force", "Number of Employees", "Number of Employers"],
        kind="line", figsize=(5, 5))
ax2.set(xlabel='Year', ylabel='Number of People (10,000)')
#plt.savefig('C:/Users/Hyunjin/Desktop/Personal_Project/plots/Year_Numbers.png', bbox_inches = "tight")