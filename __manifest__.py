# -*- coding: utf-8 -*-
{
  "name" : "InfoSaône - Module iCom-Project",
  "version" : "0.1",
  "author" : "InfoSaône",
  "category" : "InfoSaône/iCom",


  'description': """
InfoSaône / Module Project pour i-com
===================================================
""",
    'maintainer': 'InfoSaône',
    'website': 'http://www.infosaone.com',

    "depends" : ["base","analytic","project","hr_timesheet"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "security/ir.model.access.csv",
        "icom_project_view.xml",
        "icom_account_view.xml",
        "icom_crm_view.xml",
        "menu.xml"
    ],
    "installable": True,
    "active": True
}




