###
## Title: Politrade
## Description: Scrapes politician trade data from capitaltrades.com, provides registered accounts with the politician trades in a user-friendly format.

## Prerequisites:
Python
NextJS

## Installation Steps:
1. Clone the repository
    a) git clone https://github.com/JustAnotherMango/Politrade.git
    b) Alternatively, use a tool such as github desktop or sourcetree

## Environment Variables
A .env file is required for the program to run properly. It should be stored in src/app and hold a "SECRET_KEY" value.

    SECRET_KEY=

This is the only required environment variable.

## Codebase Structure
├── .next                               # Folder containing NextJS files, do not edit
├── .vs                                 # Folder containing VS code files, do not edit
├── node_modules                        # Folder containing the tools used, do not edit
├── public                              # Static files
├── SQLIterations                       # SQL queries for creating the database tables
├── src                                 # Source Code
│   ├── app                             # Contains the bulk of the website, including frontend and backend
│   │   ├── _pycache_                   # Holds files corresponding to tokens when a user logs in
│   │   ├── about                       # Contains the about page file 
│   │   │   ├── page.tsx                # About page file
│   │   ├── api                         # Contains the routes for login, logout, and /me. These are handled automatically
│   │   ├── context                     # Provides logged in user info such as username
│   │   ├── login                       # Contains the login page file
│   │   │   ├── page.tsx                # Login page file 
│   │   ├── politicians                 # Contains the politicians pages
│   │   │   ├── [name]                  # Necesary for each politician to have their own pages generate dynamically
│   │   │   │   └── page.tsx            # This file represents each politician's individual page
│   │   │   └── page.tsx                # This is the politician search page
│   │   ├── registration                # Contains the registration page file
│   │   │   └── page.tsx                # Registration page file
│   │   ├── .env                        # This is where the .env file should go, and should only contain a SECRET_KEY value
│   │   ├── auth.py                     # Creates tokens for user sessions when someone logs in with a valid account
│   │   ├── favicon.ico                 # Unused icon
│   │   ├── globals.css                 # Contains global CSS values for tailwind
│   │   ├── layout.tsx                  # File with global layouts applied to every page, which we only used for the global header
│   │   ├── main.py                     # API file for communication between the frontend and the database
│   │   └── page.tsx                    # The main landing page/home page for the website
│   ├── backend                         # Requests the backend localhost
│   ├── components                      # Contains components for things such as the UI
│   │   └── ui                          # Folder for holding UI components
│   │       ├── button.tsx              # Button component that is used throughout the website
│   │       ├── card.tsx                # Card components used for creating the politician profiles
│   │       ├── Header.tsx              # Header component with login persistence incorporated
│   │       ├── input.tsx               # Used for input fields in pages such as login and registration
│   │       ├── LoginForm.tsx           # Login component that is used in the login page
│   │       ├── PoliticianSearch.tsx    # Search bar and filters that are used on the politician search page
│   │       └── RegistrationForm.tsx    # Registration form used in the registration page
│   └── lib                             # File used by tailwind
├── Trade Scraper                       # Folder containing the scraper program
│   └── datascraper.py                  # Scraper program, designed to scrape information from capitaltrades.com
├── .gitignore                          # Files used to tell github what files to ignore in pushes to remote branches
├── components.json                     # Routes tailwind to the css globals file
├── eslint.config.mjs                   # Configuration file for eslint
├── next-env.d.ts                       # NextJS file, do not edit
├── next.config.ts                      # Configuration file for NextJS, do not edit
├── package-lock.json                   # Contains information on downloaded packages
├── package.json                        # Shows versions of all tools used
├── postcss.config.mjs                  # Enables tailwind
├── README.md                           # You are here! Provides information and instructions for the repository
└── tsconfig.json                       # Configuration file for typescript

Every webpage needs to be named page.tsx, and every webpage excluding the home page needs to be in a folder. The folder needs to be named after what the route to that webpage should be, for example the login page is in a folder named "login", which automatically sets the route to that page as /login.

These webpage files utilize react, so the top of the file will contain any functionality with javascript, and the bottom return statement is what contains all of the HTML and CSS. This project utilizes tailwind, so all of the HTML and CSS will reflect that.

## Local Environment Setup
1. Setup local database
    a) MySQL workbench is reccomended
    b) Run the SQL commands listed in iteration4.sql which is stored within the SQLIterations folder
2. Run the scraper program
    a) You will be prompted with 6 options
    b) If this is the first time everything is being set up, run 1: Full Insert
    c) If you are simply updating trades for politicians that are already in the database, run 2: Update Trades
    d) Run 3: Fetch Historical so the program can gather information for the ROI values
    e) Run 4: ROI by Pairs to calculate and store the ROI information for each politician
3. Start the backend
    a) Run the following command: python main.py
4. Start the frontend
    a) Run the following command: npm run dev
5. The website should be up and running at this point, if it is not then please make sure everything listed above is installed, and all prerequisites are met.
    a) Visit http://localhost:3000 to view the frontend
    b) Visit http://localhost:5000 to view the backend

## Contributions