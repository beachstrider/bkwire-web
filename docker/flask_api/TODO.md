## TODO:
Start the App re-write - modularized so we can implement in pieces

Concept:
Update the S3 Bucket Location for better house keeping and file tracking
e.g., #wawbk/2023/10353/petition/wawbk.2023.10353.p-679192.pdf
#wawbk/2023/10353/creditors/c-679193[0].pdf
#wawbk/2023/10353/files/f-679197.pdf
Each service should simply return the result, helper scripts will handle logic/call parsers as needed to format/manipulate data
Each service should have a config file for all variables that are configurable/changed in the future
Improve the logging/debug information to be more helpful in troubleshooting events
Improve the process as follows:
- daily batch report is ran, downloaded and saved in S3 bucket for future reference
-- daily batach will check if existing report can be loaded instead(can be a flag or just part of the logic)

#daily batch notifies report is ready for parse/case scrape
- report is parsed and case information is scraped and stored in the database(all potential cases to parse)
-- ALL case details

#reports notifies case examination and setup for detailed parsing
- using report info, check case information and details
acquire the following information:
(I think we can get all this information from Docket Report)
--Debtor information/EIN
---Adddress
---EIN
---Alias
---Attorneys
---Case Summary
--Creditors Associated < Except this - need to query specific >
--Sub Chapter V
--Associated Cases < Except this - need to query specific >
--Chapter Filing(7/11 - Non-Individual)
--Docket Info Updates
# Save the above set to the database company/company_info/debtor_info/case_info #
# Use case name AND number to determine duplicates
#query for cases to begin parsing 201/204/206 datasets
- Determine which cases are parent / children - DO NOT PARSE 204 data, just show parent data.
- Parse 201 data
# Save the above set to DB
- Parse 204 data
- Scrub and Title this data

# Run report and Stats
# Highlight warnings/errors

Modules(Build as Classes):
-company
--config
--address_parser
--company_scrub
--company_slug
--company_parser

-aws
--config
--textrac_parsing
--copy_s3_objects

-bkwdatetime
--date_time

-database
--config
--db_commit_query
---fetch/fetchmany/commit
--db_backup_to_s3

-industry
--config
--scraper

-news
--config
--*all industry news modules

-notifications
--config
--email
--phone

-pacer
--config
--login
--parsing
--refresh
--file downloads

** Add additional PACER parsing features(creditors, judges, etc)
** Improve the notifications/email(need to reduce copy/paste)
** Imporve the DB process and connections(need to reduce copy/paste)
** sub_apps - bkw_app_api_funcs (need to reduce copy/paste, improve template flow and CC generation)
Check Team Add function - check against "Max Team Allowed" in DB and return error

BEFORE daily email is sent - verify "Success Daily Run" flag = True
*Job can recheck every 1hr or so

# INFRA STR #
Server Logging
App Logging
Error Alerting
Downtime monitoring
Status Reports

RUNDECK JOBS
-- Run PACER login every 4 hours

Remaining Tasks:
- Fix daily_import for 205/Sub Chap V case to show accordingly
- Update Pacer Files to have more descriptive naming
- Team Member Email (Setup Constant Contact to send Team Member email when newly added to list)


March 1st - Go Date LIVE!

Write a script to fix any pending cases (files not in bkw_files)
Send James - All pending info for population
Send James - All Impacted Business for BKwire


***
Ind - 199 - Annual 1 month free
team - 399 (3 users) + 100(per comp user) Annual 1 month free
mvp - 999 (1 user) Annual 1 month free - **90 day cancellation ?!?!
***

Ind/Team - Watchlist - 5
-- FTX (NO CREDITORS) 2X WEEK - wed/fri
IMPACTED BUSINESS ALERT
Once they are found no more auto case refreshes
MVP - Watchlist Daily
204 notification and docket update notification 
Docket refresh ONLY for MVP

Need some updates to constant contact to put companies as Tag
Update constant contact - Interested industries(1-3) as custom field

SELECT  * FROM bankrupcty_filing_data
WHERE id NOT IN
(
SELECT  bfd_id
FROM bkw_files
)

Product Tour Popup - first login

Docket Update Email Template
Team Leader Email - Add video
Team Member Email - Ready to Go

Activity - Add date instead of Days Ago.

Feature Requests:
Sign Up - Slow performance*
Sub Chapter 5 - call those out(similar to involuntary)
Graph - interactive, filters cases by that day
News - Set your own buckets/industry
Case Number as Column and Make it searchable
Claims Agent - ??

Filings 30/60/90 - Graphs
