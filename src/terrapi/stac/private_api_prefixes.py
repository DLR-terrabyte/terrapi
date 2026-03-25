import jwt

def get_valid_private_api_prefixes(auth_token)->tuple[list[str],list[str]]:
    decoded = jwt.decode(auth_token, options={"verify_signature": False})
    rw_prefix = []
    ro_prefix = []
    user_id=decoded.get("preferred_username")
    if user_id:
        rw_prefix.append(user_id+".")
    groups=decoded.get("groups")
    if groups:
        for g in groups:
            if g.startswith("/dss/"):
                g = g.replace("/dss/","")
                if "-dss-" in g and not g.endswith("-mgr"):
                    if g.endswith("-ro"):
                        ro_prefix.append(g.replace("-ro","."))
                    else:
                        rw_prefix.append(g+".") 
        rw_prefix.sort()
        ro_prefix.sort()
    return rw_prefix, ro_prefix
