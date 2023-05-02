import ads
import matplotlib.dates as mdates
import pandas as pd
import matplotlib.pyplot as plt
from ads_fields import FIELDS

def query_ads():
    qry = ads.SearchQuery(q='full:"lightkurve" AND year:2017-2050', rows=999999, fl=FIELDS)
    papers = [q for q in qry ]

    dates = [p.date for p in papers[::-1]]
    titles = [p.title[0] for p in papers[::-1]]
    years = [p.year for p in papers[::-1]]
    authors = [p.first_author_norm for p in papers[::-1]]
    bibcodes = [p.bibcode for p in papers[::-1]]
    pubs = [p.pub for p in papers[::-1]]
    cite_count = [p.citation_count for p in papers[::-1]]

    df = pd.DataFrame({'year': years,
                    'date': pd.to_datetime(dates),
                    'title': titles,
                    'author': authors,
                    'bibcode': bibcodes,
                    'pub': pubs,
                    'cite_count': cite_count})
    # Filter out Zenodo entries and AAS Abstracts
    mask = ~df.pub.str.contains("(Zenodo)|(Abstracts)")
    # Sort by date and reset index
    df = df[mask].sort_values('date', ascending=False).reset_index(drop=True)

    return df

def make_recent_table(df):
    # Save raw stats
    df.to_csv('stats.csv')

    ## Make a markdown table
    most_recent = df.sort_values('date', ascending=False).head(5)
    most_recent = most_recent.rename(columns={'date': 'Date', 'title': 'Title', 'author': 'Author'})
    link_title = []
    for index, row in most_recent.iterrows():
        link_title.append(f'[{row.Title}](https://ui.adsabs.harvard.edu/abs/{row.bibcode}/abstract)')
    most_recent['Title'] = link_title
    most_recent['Date'] = most_recent['Date'].dt.date
    recent_table = most_recent[['Date', 'Title', 'Author']]
    return recent_table

def make_readme(md, path='README.md'):
    readme_str = f'''
    <h1>Lightkurve statistics</h1>
    
    ![publications](lightkurve-publications.png)  
    
    {md}
    '''
    text_file = open(path, "w")
    n = text_file.write(readme_str)
    text_file.close()

def make_plot(df, path='out/lightkurve-publications.png'):
    # Make a plot
    x = pd.date_range('2018-01-01T00:00:00Z', df.date.max(), freq='1M')
    y = [len(df[df.date < d]) for d in x]

    fig, ax = plt.subplots(figsize=[9, 5])
    plt.plot(x, y, marker='o', c='k')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel("Publications", fontsize=12)
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.savefig(path)
    plt.close()

if __name__ == '__main__':
    df = query_ads()
    # Save entire table
    df.to_csv('out/statistics.csv')

    # get recent publications
    recent = make_recent_table(df)

    # Make the plot
    make_plot(df)

    # Now save the readme
    make_readme(recent.to_markdown())