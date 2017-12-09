# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

import datetime
from dateutil import parser


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order='create_date desc'

    @api.multi
    @api.depends('date')
    def _week_date(self):
        for rec in self:
            semaine=""
            # Recupère la date au format string
            s = rec.date # 2013-09-25 22:41:04
            if s:
              # Convertir la date en objet datetime
              dt = parser.parse(s)
              # Cette fonction retourne un tableau avec l'annee, la semaine et le jour dans la semaine
              if dt:
                t=dt.isocalendar()
                # Recuperation de la semaine dans le tableau
                semaine=str(t[0])+"-S"+str(t[1])
            rec.week_date = semaine


    week_date = fields.Char( compute='_week_date', string='Semaine', store=True, readonly=True)



class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
 
    date_start = fields.Date(string='Start Date')
    date = fields.Date(string='Expiration Date', index=True, track_visibility='onchange')
    user_id = fields.Many2one('res.users','User')
    
    
class ProjectProject(models.Model):
    _inherit = 'project.project'
     
    date_start = fields.Date(related='analytic_account_id.date_start', string='Start Date', store=True)
    date = fields.Date(related='analytic_account_id.date',string='Expiration Date', index=True, track_visibility='onchange', store=True)

        
        
