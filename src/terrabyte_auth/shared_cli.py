




@click.command()
@click.option("-f", "--force", is_flag=True, show_default=False, default=False, help="Force new login, even if valid Refresh Token stored" )
@click.option("--valid", is_flag=True, type=bool,  show_default=False,default=False, help="Will print till when the Refresh token is valid.")
@click.option( "--delete", is_flag=True, show_default=False, help="Delete existing Refresh Token. Will remove the Refresh token if it exists and then exit", default=False )
@click.option("-d", "--days", type=int,  show_default=False,default=0,help="Min Nr of days the Token still has to be valid. Will refresh Token if it expires earlier")
@click.option("-h", "--hours", type=int, show_default=False, default=0,help="Min Nr of hours the Token still has be valid. Will refresh Token if it expires earlier")
@click.option("-t","--till", type=click.DateTime(), default=datetime.now(), help="Date the Refresh token has to be still be valid. Will refresh Token if it expires earlier")
@click.pass_context
def login(ctx: dict, force: bool = False, delete: bool = False, days: int = 0, hours: int = 0, till: datetime = datetime.now() , valid: bool = False ):
    """Interactively login via 2FA to obtain refresh Token for the API. 
    A Valid Refresh token is needed for all the other sub commands
    It is recommended to call this function first to make sure you have a valid token for the remainder of your job. This allows the other subcommands to run non inveractive    
    """
    stac_issuer=_get_issuer(ctx.obj['privateStacUrl'])
    till = max(till, datetime.now()+timedelta(hours=hours, days=days)) 
    if valid:
        validity= ctx.obj['tokenStore'].get_expiry_date_refresh_token(stac_issuer, ctx.obj['ClientId'])
        if validity:
            click.echo(f"Refresh Token valid till: {validity.astimezone()}")
        else:
            click.echo("No valid Refresh Token on file") 
        return 
    if delete:
        if ctx.obj['DEBUG']:
            click.echo("Deleting Refresh Token")
        ctx.obj['tokenStore'].delete_refresh_token(stac_issuer, ctx.obj['ClientId'])
        return
    tokens = _get_auth_refresh_tokens(ctx,force_renew=force)
    if tokens is None:
        exit(1)
