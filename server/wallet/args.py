from webargs import fields, validate

history_args = {
    "addresses": fields.List(fields.Str, missing=[], validate=validate.Length(min=1, max=20)),
    "count": fields.Int(missing=100, validate=validate.Length(min=1, max=500)),
    "before": fields.Str(missing=None)
}
