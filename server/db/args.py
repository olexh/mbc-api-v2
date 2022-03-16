from webargs import fields, validate

page_args = {
    "page": fields.Int(missing=1, validate=validate.Range(min=1)),
    "size": fields.Int(missing=10, validate=validate.Range(min=1, max=100))
}

broadcast_args = {
    "raw": fields.Str(required=True)
}

tokens_args = {
    "page": fields.Int(missing=1, validate=validate.Range(min=1)),
    "search": fields.Str(missing=None)
}

chart_args = {
    "resolution": fields.Int(missing="1D", validate=lambda r: r in ["1D", "1M", "1Y"]),
    "currency": fields.Str(missing="AOK")
}
