# Investing

This project contains different decision support tools for various types of investments. These tools allow the analysis of assets based on different approaches of renowned investors:
* [Warren Buffet](https://www.amazon.fr/Warren-Buffett-Interpretation-Financial-Statements/dp/1849833192/ref=sr_1_25?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2E39FUGQ1KHV4&keywords=warren+buffet&qid=1645034353&sprefix=warren+buffet%2Caps%2C79&sr=8-25)
* [Peter Lynch](https://www.amazon.fr/One-Wall-Street-Peter-Lynch/dp/0743200403/ref=sr_1_2?keywords=peter+lynch&qid=1645034506&sprefix=peter+lync%2Caps%2C111&sr=8-2)
* [Christopher Mayer](https://www.amazon.fr/100-Baggers-Stocks-100-1/dp/1621291650/ref=sr_1_1?crid=AZJTGL0WSHZC&keywords=chris+mayer&qid=1645034599&sprefix=CHRIS+MAYER%2Caps%2C134&sr=8-1)
* [Jim Slater](https://www.amazon.fr/Zulu-Principle-Extraordinary-Profits-Ordinary/dp/1905641915/ref=sr_1_1?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=GWUFIBSJ4B4G&keywords=jim+slater&qid=1645034646&sprefix=jim+slater%2Caps%2C94&sr=8-1)
* Etc.

## Get Started

* Download and install [python](https://www.python.org/downloads/)
* Download and copy [chromedriver](https://chromedriver.chromium.org/downloads)
If you're on Windows you can copy/paste it under 'c:/chromedriver' and [add it to your environment variables](https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html#GUID-DD6F9982-60D5-48F6-8270-A27EC53807D0)
> **Note:** The version of the chromedriver should match your browser version.

### Install Dependencies

* Update **'pip'**:
```python -m pip install --upgrade pip```
* Install **'tabulate'**:
```pip install tabulate```
* Install **'Beautiful Soup'**:
```pip install bs4```
* Install **'lxml'**:
```pip install lxml```

### Usage
```python fundamentals.py <ISIN>```

ex:

```python fundamentals.py FR0000075442```

#### Output
```
Fundamental analysis of Groupe LDLC SA (ALLDL) :


* Change in net income:

+     2018        2019       2020        2021  Est. 2022
---------  ----------  ---------  ----------  -----------
4.721e+08  5.0749e+08  4.934e+08  7.2407e+08  775.51M

Profitability:
Gross margin (TTM): 17.91%
Operating margin (TTM): 8.64%
Net margin (TTM): 5.83%

Overral financial performance:
EV/EBITDA: 3.50 -> excellent
EBIT/EV: 0.26x
P/E Ratio: 5.55 -> excellent

Management effectivness:
ROA (TTM): 15.12% -> excellent
ROCE (TTM): 52.85% -> excellent
ROE (TTM): 41.55% -> excellent

Balance sheet:
Current ratio (TTM): 1.30 -> bad

The stock value of Groupe LDLC SA (ALLDL) does not meet Warren Buffet's selection criteria

Recommendation 4.00/10
Pros:
-The net earnings follow an upward trend over a period of 4 years (33.88%)
-Tangible fixed assets (PPE) are reasonable: the tangible fixed assets to net income ratio is less than 2 (0.27)
-The company is in a strong position, its long-term debt to net income ratio is less than 4 (0.21)
-Capital expenditures are reasonable, they represent less than 50% of the net income (19.78%)
Cons:
-The gross margin is lower than 40% (17.91%)
-The net margin is lower than 20% (5.83%)
-Selling, General and Administrative expenses represent more than 30% of the gross margin (44.54%)
-The current ratio is lower than 1.5 (1.30)
-Inventories do not move in line with profits (to be taken into account only if the products sold may become obsolete)-The company draws on it's cash

The stock value of Groupe LDLC SA (ALLDL) does not meet Chris Mayer's selection criteria

Recommendation 0.00/10
Pros:
Cons:
-Mayer may not consider this company as a potential 100-bagger

The stock value of Groupe LDLC SA (ALLDL) meets some of Jim Slater's selection criteria

Recommendation 6.67/10
Pros:
-The annual earnings growth rate is higher than 15% (33.88%)
-The return on capital employed is higher than 20% (52.85%)
Cons:
-Slater prefers smallcaps
```

> **Note:** For now only french equities are supported by default. If you want to add support to other companies/countries you need to add them under **equities** folder.
