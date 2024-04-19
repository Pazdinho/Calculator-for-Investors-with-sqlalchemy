
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, create_engine
from sqlalchemy.orm import sessionmaker, Query
import csv

columns = ('ticker', 'name', 'sector', 'ebitda', 'sales', 'net_profit', 'market_price', 'net_debt', 'assets', 'equity','cash_equivalents', 'liabilities')
columns_names = ('ticker', 'name', 'sector', 'ebitda', 'sales', 'net profit', 'market price', 'net_debt', 'assets', 'equity','cash equivalents', 'liabilities')

def main_menu():
    print("Welcome to the Investor Program!\n")

    while True:
        print("MAIN MENU\n0 Exit\n1 CRUD operations\n2 Show top ten companies by criteria\n\nEnter an option:")
        option = input()
        if option == '0':
            print('Have a nice day!')
            break
        elif option == '1':
            crud()
        elif option == '2':
            top_ten_menu()
        else:
            print('Invalid option!\n')


def crud():
    print("CRUD MENU\n0 Back\n1 Create a company\n2 Read a company\n3 Update a company\n4 Delete a company\n5 List all companies\n\nEnter an option:")
    option = input()
    while True:
        if option == '0':
            break
        elif option == '1':
            create()
        elif option == '2':
            read_upt_del(option)
        elif option == '3':
            read_upt_del(option)
        elif option == '4':
            read_upt_del(option)
        elif option == '5':
            list_all_companies()
        else:
            print('Invalid option!\n')

def create():
    data = create_dict()

    with Session() as session:
        session.add(Companies(**{key: value for key, value in data.items() if key in ('ticker', 'name', 'sector')}))
        session.add(Financial(**{key: value for key, value in data.items() if key not in ('name', 'sector')}))
        session.commit()
        print("Company created successfully!")


def create_dict():
    mdict = {}
    for c,cm in zip(columns,columns_names):
        if c == 'ticker':
            value = input("Enter ticker (in the format 'MOON')")
        if c == 'name':
            value = input("Enter company (in the format 'Moon Corp')")
        if c == 'sector':
            value = input("Enter industries (in the format 'Technology')")
        else:
            value = input(f"Enter {cm} (in the format '987654321')")
        mdict[f'{c}'] = value
        return mdict

def read_upt_del(option):
    with Session() as session:

        name = input("Enter company name: ")
        query = session.query(Companies).filter(Companies.name.like(f"%{name}%"))

        if bool(session.query(Companies).filter(Companies.name.like(f"%{name}%")).first()):
            mydict = {}
            for i, company in enumerate(query):
                mydict[i] = [company.ticker, company.name]
                print(i, company.name)

            comp_num = int(input("Enter company number:"))

            if option == "2":
                myquery = session.query(Financial).filter(Financial.ticker == mydict[comp_num][0])
                indicators(myquery, mydict[comp_num])
                session.commit()
            elif option == "3":
                session.query(Financial).filter(Financial.ticker == mydict[comp_num][0]).update(update_dict())
                session.commit()
                print('Company updated successfully!')
            elif option == "4":
                session.query(Companies).filter(Companies.ticker == mydict[comp_num][0]).delete()
                session.query(Financial).filter(Financial.ticker == mydict[comp_num][0]).delete()
                session.commit()
                print('Company deleted successfully!')

        else:
            print("Company not found!")


def update_dict():
    mdict = {}
    for c,cm in (columns[3:], columns_names[3:]):
        value = input(f"Enter{cm} (in the format '987654321')")
    mdict[f'{c}'] = value
    return mdict


def indicators(query, mydict):
    for company in query:
        print(mydict[0], mydict[1])
        print(f"P/E ={calculate(company.market_price, company.net_profit)}")
        print(f"P/S ={calculate(company.market_price, company.sales)}")
        print(f"P/B ={calculate(company.market_price, company.assets)}")
        print(f"ND/EBITDA ={calculate(company.net_debt, company.ebitda)}")
        print(f"ROE ={calculate(company.net_profit, company.equity)}")
        print(f"ROA ={calculate(company.net_profit, company.assets)}")
        print(f"L/A ={calculate(company.liabilities, company.assets)}")

def calculate(num1: float, num2: float):
    value = round(num1 / num2, 2)
    return value

def list_all_companies():
    with Session() as session:
        print("COMPANY LIST")
        for company in session.query(Companies).order_by(Companies.ticker):
            print(company.ticker, company.name, company.sector)
def top_ten_menu():
    print("TOP TEN MENU\n0 Back\n1 List by ND/EBITDA\n2 List by ROE\n3 List by ROA\n\nEnter an option:")
    option = input()
    if option == '0':
        print('Have a nice day!')
    elif option == '1':
        parameters(option)
    elif option == '2':
        parameters(option)
    elif option == '3':
        parameters(option)
    else:
        print('Invalid option!')


def parameters(option):
    nd = {"mformula": Financial.net_debt / Financial.ebitda}
    roe = {"mformula": Financial.net_profit / Financial.equity}
    roa = {"mformula": Financial.net_profit / Financial.assets}
    with Session() as session:
        if option == '1':
            print('TICKER ND/EBITDA')
            query = session.query(Financial.ticker, nd.get("mformula").label("parametr")).order_by(nd.get("mformula").label("parametr").desc()).limit(10)
            for para in query:
                print(f"{para.ticker} {float('{:.2f}'.format(para.parametr))}")
        elif option == "2":
            print('TICKER ROE')
            query = session.query(Financial.ticker, roe.get("mformula").label("parametr")).order_by(roe.get("mformula").label("parametr").desc()).limit(10)
            for para in query:
                print(f"{para.ticker} {float('{:.2f}'.format(para.parametr))}")
        elif option == "3":
            print('TICKER ROA')
            query = session.query(Financial.ticker, roa.get("mformula").label("parametr")).order_by(roa.get("mformula").label("parametr").desc()).limit(10)
            for para in query:
                print(f"{para.ticker} {float('{:.2f}'.format(para.parametr))}")


Base = declarative_base()
engine = create_engine("sqlite:///investor.db")
Session = sessionmaker(bind=engine)

class Companies(Base):
    __tablename__ = "companies"

    ticker = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)


class Financial(Base):
    __tablename__ = "financial"

    ticker = Column(String, primary_key=True)
    ebitda = Column(Float, default=None)
    sales = Column(Float, default=None)
    net_profit = Column(Float, default=None)
    market_price = Column(Float, default=None)
    net_debt = Column(Float, default=None)
    assets = Column(Float, default=None)
    equity = Column(Float, default=None)
    cash_equivalents = Column(Float, default=None)
    liabilities = Column(Float, default=None)


def clean_data(dict):
    return {keys: values if values else None for keys, values in dict.items()}

def load_data():
    with open("financial.csv") as financial, open("companies.csv") as companies, Session() as session:
        companies = csv.DictReader(companies)
        financial = csv.DictReader(financial)

        for data in companies:
            if not bool(session.query(Companies).filter(Companies.ticker == data.get("ticker")).first()):
                session.add(Companies(**clean_data(data)))
        for data in financial:
            if not bool(session.query(Financial).filter(Financial.ticker == data.get("ticker")).first()):
                session.add(Financial(**clean_data(data)))

        session.commit()

Base.metadata.create_all(engine)
load_data()
main_menu()
