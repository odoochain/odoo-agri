from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_date


class Farm(models.Model):
    _name = 'agri.farm'
    _description = 'Farm'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, create_date desc'
    _check_company_auto = True

    active = fields.Boolean('Active', default=True, tracking=True)
    name = fields.Char('Name', required=True)
    partner_id = fields.Many2one('res.partner',
                                 string='Partner',
                                 ondelete='cascade',
                                 required=True,
                                 check_company=True)
    company_id = fields.Many2one('res.company',
                                 required=True,
                                 default=lambda self: self.env.company)
    area_ha = fields.Float('Hectares', digits='Hectare')
    boundary = fields.GeoPolygon('Boundary', srid=4326, gist_index=True)
    has_boundary = fields.Boolean('Has Boundary',
                                  compute='_compute_has_boundary',
                                  default=False)
    farm_field_ids = fields.One2many(comodel_name='agri.farm.field',
                                     inverse_name='farm_id',
                                     string='Fields',
                                     copy=True)
    farm_parcel_ids = fields.One2many(comodel_name='agri.farm.parcel',
                                      inverse_name='farm_id',
                                      string='Parcels',
                                      copy=True)
    farm_version_id = fields.Many2one('agri.farm.version',
                                      'Farm Version',
                                      ondelete='cascade',
                                      required=True,
                                      check_company=True)

    @api.onchange('boundary')
    def _compute_has_boundary(self):
        for farm in self:
            farm.has_boundary = True if farm.boundary else False

    @api.constrains('name')
    def constrains_name(self):
        domain = [('farm_version_id', '=', self.farm_version_id.id),
                  ('active', '=', True), ('name', 'ilike', self.name)]
        if self.id:
            domain.append(('id', '!=', self.id))
        farm = self.env['agri.farm'].search(domain, limit=1)
        if farm:
            raise ValidationError(_('Duplicate Farm name'))

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for farm in self:
            farm.farm_version_id = farm.partner_id.farm_version_id if farm.partner_id else False

    def name_get(self):
        return [(farm.id, "{} ({:.3f} ha)".format(farm.name, farm.area_ha))
                for farm in self]


class FarmField(models.Model):
    _name = 'agri.farm.field'
    _description = 'Farm Field'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, create_date desc'

    active = fields.Boolean('Active', default=True, tracking=True)
    name = fields.Char('Name', required=True, tracking=True)
    area_ha = fields.Float('Hectares', digits='Hectare', tracking=True)
    boundary = fields.GeoPolygon('Boundary', srid=4326, gist_index=True)
    has_boundary = fields.Boolean('Has Boundary',
                                  compute='_compute_has_boundary',
                                  default=False)
    established_date = fields.Date('Established Date', tracking=True)
    farm_id = fields.Many2one('agri.farm',
                              'Farm',
                              ondelete='cascade',
                              required=True)
    farm_version_id = fields.Many2one(related='farm_id.farm_version_id',
                                      readonly=True)
    crop_potential_id = fields.Many2one('agri.crop.potential',
                                        'Crop Potential',
                                        tracking=True)
    soil_effective_depth_id = fields.Many2one('agri.soil.effective.depth',
                                              'Effective Depth',
                                              tracking=True)
    irrigated = fields.Boolean('Irrigated', default=False, tracking=True)
    irrigation_type_id = fields.Many2one('agri.irrigation.type',
                                         'Irrigation Type',
                                         tracking=True)
    land_use_id = fields.Many2one('agri.land.use',
                                  'Land Use',
                                  required=True,
                                  tracking=True)
    soil_texture_id = fields.Many2one('agri.soil.texture',
                                      'Soil Texture',
                                      tracking=True)
    terrain_id = fields.Many2one('agri.terrain', 'Terrain', tracking=True)
    water_source_id = fields.Many2one('agri.water.source',
                                      'Water Source',
                                      tracking=True)

    @api.onchange('boundary')
    def _compute_has_boundary(self):
        for field in self:
            field.has_boundary = True if field.boundary else False

    @api.constrains('name')
    def constrains_name(self):
        for farm in self:
            domain = [('farm_id', '=', farm.farm_id.id), ('active', '=', True),
                    ('name', 'ilike', farm.name)]
            if farm.id:
                domain.append(('id', '!=', farm.id))
            field = self.env['agri.farm.field'].search(domain, limit=1)
            if field:
                raise ValidationError(_('Duplicate Field name'))

    @api.onchange('irrigation_type_id', 'land_use_id')
    def onchange_irrigated(self):
        for field in self:
            field.irrigated = True if (field.land_use_id
                                       and field.land_use_id.irrigated
                                       ) or field.irrigation_type_id else False

    def name_get(self):
        return [(field.id, "{} ({:.3f} ha)".format(field.name, field.area_ha))
                for field in self]


class FarmParcel(models.Model):
    _name = 'agri.farm.parcel'
    _description = 'Farm Parcel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, create_date desc'

    name = fields.Char('Name', required=True)
    short_name = fields.Char('Short Name', required=True)
    code = fields.Char('Code', required=True)
    country_id = fields.Many2one('res.country', string='Country')
    area_ha = fields.Float('Hectares', digits='Hectare', tracking=True)
    boundary = fields.GeoPolygon('Boundary', srid=4326, gist_index=True)
    has_boundary = fields.Boolean('Has Boundary',
                                  compute='_compute_has_boundary',
                                  default=False)
    farm_id = fields.Many2one('agri.farm',
                              'Farm',
                              ondelete='cascade',
                              required=True)
    farm_version_id = fields.Many2one(related='farm_id.farm_version_id',
                                      readonly=True)
    land_cover_ids = fields.One2many(comodel_name='agri.land.cover',
                                     inverse_name='farm_parcel_id',
                                     string='Land Cover',
                                     copy=True)

    @api.onchange('boundary')
    def _compute_has_boundary(self):
        for land in self:
            land.has_boundary = True if land.boundary else False

    @api.constrains('code')
    def constrains_code(self):
        domain = [('farm_id', '=', self.farm_id.id),
                  ('code', 'ilike', self.code)]
        if self.id:
            domain.append(('id', '!=', self.id))
        land = self.env['agri.farm.parcel'].search(domain, limit=1)
        if land:
            raise ValidationError(_('Duplicate Land'))

    def name_get(self):
        return [(land.id, "{} ({:.3f} ha)".format(land.name, land.area_ha))
                for land in self]


class FarmVersion(models.Model):
    _name = 'agri.farm.version'
    _description = 'Farm Version'
    _order = 'date DESC'
    _check_company_auto = True

    name = fields.Char('Name',
                       compute='_compute_name',
                       readonly=True,
                       stored=True)
    date = fields.Date('Date',
                       default=fields.Date.context_today,
                       required=True)
    partner_id = fields.Many2one('res.partner',
                                 string='Partner',
                                 ondelete='cascade',
                                 required=True)
    company_id = fields.Many2one('res.company',
                                 required=True,
                                 default=lambda self: self.env.company)
    parent_farm_version_id = fields.Many2one(
        'agri.farm.version',
        'Preceding Version',
        domain="[('partner_id', '=', partner_id)]")
    child_farm_version_ids = fields.Many2many(
        'agri.farm.version',
        'agri_farm_version_rel',
        'farm_version_id',
        'child_id',
        string='Following Versions',
        domain="[('partner_id', '=', partner_id), ('id', '!=', id)]")
    farm_ids = fields.One2many(comodel_name='agri.farm',
                               inverse_name='farm_version_id',
                               string='Farms',
                               copy=True)

    @api.depends('date')
    @api.onchange('date')
    def _compute_name(self):
        for farm_version in self:
            farm_version.name = 'As of {}'.format(
                format_date(self.env, farm_version.date))

    @api.model
    def create(self, vals):
        farm_version = super().create(vals)
        if farm_version.parent_farm_version_id:
            default = {'farm_version_id': farm_version.id}
            farm_commands = []
            for farm in farm_version.parent_farm_version_id.farm_ids:
                farm_copy = farm.copy(default)
                farm_commands += [(4, farm_copy.id, 0)]
            farm_version.write({'farm_ids': farm_commands})
            farm_version.parent_farm_version_id.write(
                {'child_farm_version_ids': [(4, farm_version.id, 0)]})
            latest_farm_version = self.env['agri.farm.version'].search(
                [('partner_id', '=', farm_version.partner_id.id)],
                limit=1,
                order='date DESC')
            farm_version.partner_id.write(
                {'farm_version_id': latest_farm_version.id})
        return farm_version

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, parent_farm_version_id=self)
        return super(FarmVersion, self).copy(default)


class FarmLandUse(models.Model):
    _name = 'agri.farm.land.use'
    _description = 'Farm Land Use'
    _order = 'area_ha desc'

    land_use_id = fields.Many2one('agri.land.use',
                                  'Land Use',
                                  ondelete='cascade',
                                  required=True)
    area_ha = fields.Float('Hectares', digits='Hectare', required=True)
    farm_id = fields.Many2one('agri.farm',
                              'Parcel',
                              ondelete='cascade',
                              required=True)
