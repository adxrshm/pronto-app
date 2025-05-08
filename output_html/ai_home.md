xml version="1.0" encoding="utf-8"?

Alert Intelligence

[![Home](../resources/masterpages/home-normal.jpg "Home")](../welcome.htm)[![Refresh](../resources/masterpages/refresh.jpg "Refresh")](javascript:RefreshOnclick())[![Back](../resources/masterpages/back-normal.jpg "Back")](javascript:BackOnclick())[![Forward](../resources/masterpages/forward-normal.jpg "Forward")](javascript:ForwardOnclick())[![Remove highlight](../resources/masterpages/deletehighlight-normal.jpg "Remove Search Highlighting")](#)[![Add to favourites](../resources/masterpages/addfavourite-normal.jpg "Add Topic to Favourites")](#)[![Expand All](../resources/masterpages/expandall.jpg "Expand All")](#)[![Collapse All](../resources/masterpages/collapseall.jpg "Collapse All")](#)[![Help on Help](../resources/masterpages/about-normal.jpg "Help on Help")](../help_on_help/help_on_help.htm)[![Print](../resources/masterpages/print.jpg "Print Topic")](javascript:PrintTopic() "Print this Topic")[![Maximise](../resources/masterpages/hide-normal.jpg "Show/Hide Navigation")](#)

You are here: Alert Intelligence

# Alert Intelligence

Pronto Xi Alert Intelligence allows you to capture defined business events and [trigger](javascript:void(0);)A trigger is a routine that is automatically run (triggered) whenever a specific condition occurs. one or more predetermined actions in response to such events.

An event can be defined as a specific change, or lack of change, in data in the Pronto Xi database. Events can be captured by:

* monitoring transactions on the Pronto Xi database, for example the entry of a purchase order above a defined monetary value
* monitoring the passage of time, for example an invoice or delivery becoming overdue
* manually triggering the event from a custom program

Relevant people can be notified of captured events by a variety of methods, including:

* displaying a message box
* sending an email, SMS, or fax
* starting a workflow process or external application
* creating a log entry

A range of pre-packaged event templates that can be used as-is, or tailored to specific requirements, is provided.

You can specify the recipients of a notification either explicitly or select them dynamically; for example, by using the details stored against a sales representative, customer, or supplier.Additionally, you can tailor the content of the notification or each individual recipient and, in the case of emails, provide drillbacks to specific screens.

The Alert Intelligence module leverages the [Data triggers](../4gl_reference/reference/data_triggers.htm) feature of the Pronto [RAD](javascript:void(0);)Rapid Application Development. The Pronto Xi application development language. (Rapid Application Programming) language to execute automatically generated code after a database record is inserted, updated, or deleted.

Additional features of the Alert Intelligence module include the ability to:

* release events for self-service subscription by Pronto Xi users
* manually check for and process time-based (overdue type) events
* manually trigger events using sample or actual data
* view and customise the automatically generate dictionary trigger code in Advanced Edit mode
* enhance the content of emails to include HTML markup or the results of an SQL query

If an activation error is displayed on selecting any of the Alert Intelligence functions, contact your local Pronto Software Support Centre to obtain an activation key.

[Top^](#top)

[About the Alert Intelligence module](concept/about_alert_intelligence.htm)

[Menu functions](ref_function/menu_functions.htm)

[Using the Alert Intelligence module](task/toc_using_the_ai_module.htm)

[Print Topic](javascript:PrintTopic() "Print this Topic") |  | [Pronto Plus](# "Pronto Plus") | [Help FAQs](../help_on_help/help_on_help.htm)

© Copyright 2018 Pronto Software Limited. All rights reserved.  
Reference Manual, Version 740.4, 4GL Release 7.4v4.2  
**Trademarks**  
® Pronto, Pronto (logo), P (logo), Pronto Software, Pronto Xi, Pronto Xi Dimensions, and Pronto Enterprise Management System are trademarks registered by Pronto Software Limited (ABN 47 001 337 248) in Australia, USA and other countries.  
™- trademarks of Pronto Software Limited (ABN 47 001 337 248)  
IBM® and Cognos® are trademarks of International Business Machines Corporation.  
**Disclaimer**  
The information contained within this document is provided on an “as is” basis, is subject to change without notice, and is not warranted to be error-free.  
Each manual provides an overview of the functions available for that module based on the out-of-the-box settings. Pronto Software does not provide procedural manuals and/or work instructions due to the complex and differing nature of business models Pronto Xi currently supports. Permission is granted for information to be copied from the reference manuals for the express purpose of writing site-specific procedures/work instructions.[© 2018 Pronto Software Limited](javascript:void(0);)