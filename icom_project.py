# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import datetime
from dateutil import parser
from openerp.exceptions import Warning


is_type_projet = [
    ('maintenance', 'Maintenance'),
    ('web'        , 'Web'),
    ('i-com'      , 'i-com'),
]


class Project(models.Model):
    _inherit = 'project.project'
    _order = 'name'

    is_type_projet = fields.Selection(is_type_projet,'Type de projet')



class TaskCompteurDescription(models.TransientModel):
    _name  = 'is.project.task.compteur.description'

    commentaire = fields.Char('Description', required=False)

    @api.multi
    def demarrer_compteur(self):
        for obj in self:
            active_id=self._context['active_id']
            task=self.env['project.task'].browse(active_id)
            if task:
                vals={
                    'task_id'       : task.id,
                    'heure_debut'   : fields.datetime.now(),
                    'utilisateur_id': self._uid,
                    'commentaire'   : obj.commentaire,
                }
                new_id=self.env['is.project.task.compteur'].create(vals)


    @api.multi
    def compteur_en_cours(self):
        for obj in self:
            active_id=self._context['active_id']
            task=self.env['project.task'].browse(active_id)
            if task:
                task_id=task._compteur_en_cours()
                return {
                    'name': u'Tâches',
                    'view_mode': 'form,tree',
                    'view_type': 'form',
                    'res_id'   : task_id,
                    'res_model': 'project.task',
                    'type'     : 'ir.actions.act_window',
                }





class TaskCompteur(models.Model):
    _name  = 'is.project.task.compteur'
    _order = 'heure_debut'

    task_id        = fields.Many2one('project.task', 'Tâcĥe', required=True, ondelete='cascade', readonly=True, select=True)
    heure_debut    = fields.Datetime(string='Heure de début')
    utilisateur_id = fields.Many2one('res.users', 'Utilisateur', select=True)
    commentaire    = fields.Char(string='Description')


class Task(models.Model):
    _inherit = 'project.task'

    @api.multi
    @api.depends('date_end')
    def _week_date_end(self):
        result = {}
        for rec in self:
            semaine=""
            # Recupère la date au format string
            s = rec.date_end # 2013-09-25 22:41:04
            if s:
              # Convertir la date en objet datetime
              dt = parser.parse(s)
              # Cette fonction retourne un tableau avec l'annee, la semaine et le jour dans la semaine
              if dt:
                t=dt.isocalendar()
                # Recuperation de la semaine dans le tableau
                semaine=str(t[0])+"-S"+str(t[1])
            rec.week_date_end = semaine


    week_date_end     = fields.Char(compute='_week_date_end', string='Semaine', store=True, readonly=True)
    compteur_ids      = fields.One2many('is.project.task.compteur'  , 'task_id', u"Compteurs")
    is_type_projet    = fields.Selection(is_type_projet,'Type de projet', related='project_id.is_type_projet', store=False, readonly=True)
    is_test_report    = fields.Boolean(compute='_is_test_report', string='Test report', store=False, readonly=True)
    is_heure_depassee = fields.Float(compute='_is_heure_depassee', string='Heures dépassées', store=False, readonly=True)


    @api.multi
    def tache_en_cours_action(self):
        task_id=self._compteur_en_cours()
        if task_id:
            res={
                'name': u'Tâche en cours',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id'   : task_id,
                'res_model': 'project.task',
                'type'     : 'ir.actions.act_window',
            }
        else:
            res={
                'name': u'Tâche en cours',
                'view_mode': 'tree,from',
                'view_type': 'form',
                'res_model': 'project.task',
                'type'     : 'ir.actions.act_window',
                'domain'   : [('id','=',0)],
                'help'     : 'Aucune tâche en cours',
            }
        return res


    @api.multi
    def _compteur_en_cours(self):
        cr=self._cr
        sql="""
            select task_id
            from is_project_task_compteur
            where utilisateur_id="""+str(self._uid)+"""
        """
        cr.execute(sql)
        task_id=False
        for row in cr.fetchall():
            task_id=row[0]
        return task_id


    @api.multi
    def _is_test_report(self):
        for obj in self:
            test=False
            if obj.is_type_projet!='maintenance':
                test=True
            else:
                for line in obj.timesheet_ids:
                    if line.name==u'Report négatif trimestre précédent' or line.name==u'Report positif trimestre précédent':
                        test=True
            obj.is_test_report=test


    @api.multi
    def _is_heure_depassee(self):
        for obj in self:
            obj.is_heure_depassee=-obj.remaining_hours


    @api.multi
    def demarrer_compteur(self):
        for obj in self:
            task_id=self._compteur_en_cours()
            if task_id:
                view_id=self.env['ir.model.data'].get_object_reference('icom_project', 'is_project_task_compteur_message_form_view')
                return {
                    'name': u'Démarrer le compteur',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id'  : view_id[1],
                    'res_model': 'is.project.task.compteur.description',
                    'target'   : 'new',
                    'type'     : 'ir.actions.act_window',
                }
            return {
                'name': u'Démarrer le compteur',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'is.project.task.compteur.description',
                'target'   : 'new',
                'type'     : 'ir.actions.act_window',
            }



    @api.multi
    def arreter_compteur(self):
        for obj in self:
            for line in obj.compteur_ids:
                if self._uid==line.utilisateur_id.id:
                    debut = int(datetime.datetime.strptime(line.heure_debut, '%Y-%m-%d %H:%M:%S').strftime('%s'))
                    fin   = int(fields.datetime.now().strftime('%s'))
                    duree=(fin-debut)
                    duree=duree/3600.0
                    vals={
                        'project_id' : obj.project_id.id,
                        'task_id'    : obj.id,
                        'date'       : fields.datetime.now(),
                        'user_id'    : self._uid,
                        'unit_amount': duree,
                        'name'       : line.commentaire,
                    }
                    new_id=self.env['account.analytic.line'].create(vals)
                    line.unlink()


    @api.multi
    def reporter_solde(self):
        cr=self._cr
        for obj in self:
            if obj.is_test_report:
                raise Warning(u"Report déjà éffectué !")
            sql="""
                select remaining_hours
                from project_task
                where 
                    project_id="""+str(obj.project_id.id)+""" and
                    date_deadline<'"""+str(obj.date_deadline)+"""' 
                order by date_deadline desc limit 1
            """
            cr.execute(sql)
            test=False
            report=0.0
            for row in cr.fetchall():
                test=True
                report=row[0]
            if test==False:
                raise Warning(u"Pas de report à éffectuer (premier trimestre) !")


            name=u'Report négatif trimestre précédent'
            if report>=0.0:
                name=u'Report positif trimestre précédent'
            vals={
                'project_id' : obj.project_id.id,
                'task_id'    : obj.id,
                'date'       : fields.datetime.now(),
                'user_id'    : self._uid,
                'unit_amount': report,
                'name'       : name,
            }
            new_id=self.env['account.analytic.line'].create(vals)





    @api.model
    def create(self, vals):
        obj = super(Task, self).create(vals)
        planned_hours=vals.get('planned_hours',0)
        if planned_hours==0:
            raise Warning(u"Champ 'Heures prévues initialement' non renseigné !")
        return obj






