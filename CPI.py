import requests
import pandas as pd
import io
import re
import matplotlib.pyplot as plt
import seaborn as sns

# Over 5 years (2023, 2022, 2021, 2020, 2019)
times = ["Time=2023", "Time=2022", "Time=2021", "Time=2020", "Time=2019"]

cpi_index_over_five_yrs = pd.DataFrame()
cpi_prev_over_five_yrs = pd.DataFrame()
for time in times:
    sample_url = "http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?cdArea=13A01&cdTime=2023100000&appId=e9f38dabcf373518dda9a254c6853d706c6b6c45&lang=E&statsDataId=0003427113&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0"
    sample_url = sample_url.replace("Time=2023", time)

    response = requests.get(sample_url)

    response_string = response.text
    response_string = response_string.split("VALUE",1)[1]
    df = pd.read_csv(io.StringIO(response_string), sep=",")

    df = df.drop(columns=['\ntab_code"', 'cat01_code', 'area_code', 'Area(2020-base)', 'time_code', 'Time', 'unit', 'annotation'])
    year = re.findall(r'\d+', time)
    c_name = "CPI " + str(year[0])
    df = df.rename(columns={"Items(2020-base)": "Items", "value": c_name})
    df = df.drop_duplicates(subset=['Items', c_name])

    # CPI Index Dataframe
    cpi_index = df[df['Tabulated variable']=='Index']
    cpi_index = cpi_index.drop(columns=['Tabulated variable'])
    cpi_index = cpi_index.reset_index(drop=True)

    # CPI from the last year Dataframe
    cpi_change_from_prev_yr = df[df['Tabulated variable']=='Change from the previous period (year, fiscal year, or month)']
    cpi_change_from_prev_yr = cpi_change_from_prev_yr.drop(columns=['Tabulated variable'])
    cpi_change_from_prev_yr = cpi_change_from_prev_yr.reset_index(drop=True)
    #print("cpi from prev year length: ", len(cpi_change_from_prev_yr.index))

    if cpi_index_over_five_yrs.empty:
        cpi_index_over_five_yrs = cpi_index
        cpi_prev_over_five_yrs = cpi_change_from_prev_yr
    else:
        cpi_index_over_five_yrs = pd.merge(cpi_index_over_five_yrs, cpi_index, on="Items", how="inner")
        cpi_prev_over_five_yrs = pd.merge(cpi_prev_over_five_yrs, cpi_change_from_prev_yr, on = "Items", how="inner")

cpi_index_over_five_yrs = cpi_index_over_five_yrs.replace({"\"Soba\", Japanese noodles (eating out)": "Soba"})
cpi_index_over_five_yrs = cpi_index_over_five_yrs.dropna()
cpi_index_over_five_yrs = cpi_index_over_five_yrs.drop_duplicates(subset=["Items"])
cpi_index_over_five_yrs = cpi_index_over_five_yrs.sort_values('CPI 2023', ascending=False)
cpi_index_over_five_yrs = cpi_index_over_five_yrs.reset_index(drop=True)

cpi_prev_over_five_yrs = cpi_prev_over_five_yrs.replace({"\"Soba\", Japanese noodles (eating out)": "Soba"})
cpi_prev_over_five_yrs = cpi_prev_over_five_yrs.dropna()
cpi_prev_over_five_yrs = cpi_prev_over_five_yrs.drop_duplicates(subset=["Items"])
cpi_prev_over_five_yrs = cpi_prev_over_five_yrs.sort_values('CPI 2023', ascending=False)
cpi_prev_over_five_yrs = cpi_prev_over_five_yrs.reset_index(drop=True)


print(len(cpi_index_over_five_yrs.index))

data = cpi_index_over_five_yrs[["CPI 2023",  "CPI 2022",  "CPI 2021"]]
sns.violinplot(data=data)
plt.title("Distribution of CPI from 2021 to 2023")
plt.xlabel("Year")
plt.ylabel("CPI")
plt.savefig('C:/Users/Hyunjin/Desktop/Personal_Project/plots/violin_whole_CPI_comparisons.png', bbox_inches = "tight")

cpi_prev_over_five_yrs = cpi_prev_over_five_yrs.replace({"\"Soba\", Japanese noodles (eating out)": "Soba"})

# Top 5 CPI among the entire CPI dataset
"""nec_items_top_5 = cpi_index_over_five_yrs[:5]
times = [2023, 2022, 2021, 2020, 2019]
ax2 = nec_items_top_5.plot(x="Items", y=["CPI 2021", "CPI 2022", "CPI 2023"],
        kind="bar", figsize=(8, 5))
ax2.set(xlabel="Items", ylabel='CPI')
plt.ylim(80, 180)
plt.xticks(rotation=0)
plt.grid(axis = 'y')
plt.title("Goods with top 5 CPI growth in 2023")"""

#plt.savefig('C:/Users/Hyunjin/Desktop/Personal_Project/plots/whole_top_3_CPI_comparisons.png', bbox_inches = "tight")

# Lowest 5 CPI among the entire CPI dataset
"""nec_items_low_5 = cpi_index_over_five_yrs[-6:-1]
times = [2023, 2022, 2021, 2020, 2019]
ax2 = nec_items_low_5.plot(x="Items", y=["CPI 2021", "CPI 2022", "CPI 2023"],
        kind="bar", figsize=(8, 5))
ax2.set(xlabel="Items", ylabel='CPI')
plt.ylim(40, 120)
plt.xticks(rotation=15)
plt.title("Goods with lowest 5 CPI growth in 2023")
plt.grid(axis = 'y')"""

#plt.savefig('C:/Users/Hyunjin/Desktop/Personal_Project/plots/whole_tlow_3_CPI_comparisons.png', bbox_inches = "tight")

# Which had the biggest CPI change over years?
# Let's look into the cpi of the necessary groceries for us to live in Japan 
# https://listonic.com/basic-grocery-list/
necessary_items = pd.DataFrame()
necessary_items_over_five_yrs = pd.DataFrame()
necessary_groceries = ['Tofu', 'Fish', 'Meat', 'Egg', 'Rice', 'Dairy', 'Soba', 'Oil', 'Salt', 'Pepper', 'Vegetable', 'Soy sauce', 'Bread']
for groc in necessary_groceries:
    if necessary_items.empty:
        necessary_items = cpi_index_over_five_yrs[cpi_index_over_five_yrs['Items'].str.contains(groc)]
        necessary_items_over_five_yrs = cpi_prev_over_five_yrs[cpi_prev_over_five_yrs['Items'].str.contains(groc)]
    else:
        necessary_items = pd.concat([necessary_items, cpi_index_over_five_yrs[cpi_index_over_five_yrs['Items'].str.contains(groc)]]) 
        necessary_items_over_five_yrs = pd.concat([necessary_items_over_five_yrs, cpi_prev_over_five_yrs[cpi_prev_over_five_yrs['Items'].str.contains(groc)]]) 

necessary_items = necessary_items.sort_values('CPI 2023', ascending=False)
necessary_items = necessary_items.reset_index(drop=True)
necessary_items2 = necessary_items_over_five_yrs.sort_values('CPI 2023', ascending=False)
necessary_items2 = necessary_items2.reset_index(drop=True)

print(necessary_items)
necessary_items = necessary_items.drop(necessary_items[necessary_items['Items'] == 'Fishing rods'].index)
necessary_items['Items'].replace('Fish prepared in soy sauce', 'Fish in soy sauce', inplace=True)


# Compare rice VS bread
"""necessary_items_bread = necessary_items[necessary_items['Items'].str.contains('Bread')]
necessary_items_bread = pd.concat([necessary_items[necessary_items['Items']=='Rice'],necessary_items_bread.loc[:]]).reset_index(drop=True)
rice_list= list(necessary_items_bread.iloc[0])[1:]
sandwiches_list = list(necessary_items_bread.iloc[1])[1:]
bread_list = list(necessary_items_bread.iloc[2])[1:]
year_list = ["2019", "2020", "2021", "2022", "2023"]
print(necessary_items_bread)
plt.plot(year_list, list(reversed(rice_list)), '--go', label = "Rice",) 
plt.plot(year_list, list(reversed(sandwiches_list)), '-bo', label = "Bread like sandwiches") 
plt.plot(year_list, list(reversed(bread_list)), '-yo', label = "Bread") 
plt.legend(loc="upper left")
plt.ylim(80, 140)
plt.xlabel("Year")
plt.ylabel("CPI")
plt.xticks(rotation=0)
plt.title("Rice VS Bread(s)")
plt.grid(axis = 'y')

plt.savefig('C:/Users/Hyunjin/Desktop/Personal_Project/plots/RiceVSBreads.png', bbox_inches = "tight")"""

# Compare rice VS rice roll
"""
necessary_items_bread = necessary_items[necessary_items['Items'].str.contains('Rice')]
print(necessary_items_bread)
rice_list= list(necessary_items_bread.iloc[0])[1:]
sandwiches_list = list(necessary_items_bread.iloc[1])[1:]
year_list = ["2019", "2020", "2021", "2022", "2023"]
print(necessary_items_bread)
plt.plot(year_list, list(reversed(rice_list)), '-bo', label = "Rice ball") 
plt.plot(year_list, list(reversed(sandwiches_list)), '--go', label = "Rice") 
plt.legend(loc="upper left")
plt.ylim(80, 140)
plt.xlabel("Year")
plt.ylabel("CPI")
plt.xticks(rotation=0)
plt.title("Rice VS Rice ball")
plt.grid(axis = 'y')

plt.savefig('C:/Users/Hyunjin/Desktop/Personal_Project/plots/RiceVSRIceRolls.png', bbox_inches = "tight")"""

# Top 5 CPI 
nec_items_top_5 = necessary_items[:5]
times = [2023, 2022, 2021, 2020, 2019]
ax2 = nec_items_top_5.plot(x="Items", y=["CPI 2021", "CPI 2022", "CPI 2023"],
        kind="bar", figsize=(8, 5))
ax2.set(xlabel="Items", ylabel='CPI')
plt.ylim(80, 180)
plt.xticks(rotation=0)
plt.title("Necessary goods with top 5 CPI growth in 2023")
plt.grid(axis = 'y')

#plt.savefig('C:/Users/Hyunjin/Desktop/Personal_Project/plots/top_3_CPI_comparisons.png', bbox_inches = "tight")


# Lowest 5 CPI
nec_items_low_5 = necessary_items[-6:-1]
ax3 = nec_items_low_5.plot(x="Items", y=["CPI 2021", "CPI 2022", "CPI 2023"],
        kind="bar", figsize=(8, 5))
ax3.set(xlabel="Items", ylabel='CPI')
plt.ylim(80, 180)
plt.xticks(rotation=0)
plt.title("Necessary Goods with lowest 5 CPI growth in 2023")
plt.grid(axis = 'y')

#plt.savefig('C:/Users/Hyunjin/Desktop/Personal_Project/plots/low_3_CPI_comparisons.png', bbox_inches = "tight")


# Is there a rent?
rent = cpi_index_over_five_yrs[cpi_index_over_five_yrs['Items'].str.contains('rent')]
housing = cpi_index_over_five_yrs[cpi_index_over_five_yrs['Items'].str.contains('housing')]
