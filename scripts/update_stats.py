"""Writes assets/stats.svg from GitHub GraphQL data (last 12 months)."""
import json, os, urllib.request
from datetime import datetime, timedelta, timezone
Q="""query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){
 repositories(ownerAffiliations:OWNER,privacy:PUBLIC){totalCount}
 contributionsCollection(from:$f,to:$t){totalCommitContributions totalPullRequestContributions totalIssueContributions}}}"""
def fetch(login,token):
    t=datetime.now(timezone.utc); f=t-timedelta(days=365)
    body=json.dumps({"query":Q,"variables":{"l":login,"f":f.isoformat(),"t":t.isoformat()}}).encode()
    r=urllib.request.Request("https://api.github.com/graphql",body,{"Authorization":"bearer "+token,"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r))["data"]["user"]
def compute(u):
    c=u["contributionsCollection"]
    return {"Public repositories":u["repositories"]["totalCount"],"Commits":c["totalCommitContributions"],
            "Pull requests":c["totalPullRequestContributions"],"Issues":c["totalIssueContributions"]}
def svg(vals,note):
    F="font-family=\"-apple-system,'Segoe UI',Helvetica,Arial,sans-serif\""
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 130" width="880" height="130" role="img" aria-label="GitHub activity, last 12 months"><rect x="1" y="1" width="878" height="128" rx="6" fill="#0b1426" stroke="#2a3f66" stroke-width="2"/>']
    for i,(k,v) in enumerate(vals.items()):
        x=40+i*210
        out.append(f'<text x="{x}" y="64" {F} font-size="36" font-weight="700" fill="#e6edf3">{v}</text><text x="{x}" y="90" {F} font-size="15" fill="#9db0cc">{k}</text>')
    out.append(f'<text x="40" y="116" {F} font-size="13" fill="#9db0cc">{note}</text></svg>')
    return "".join(out)
if __name__=="__main__":
    v=compute(fetch(os.environ["GITHUB_REPOSITORY_OWNER"],os.environ["GH_TOKEN"]))
    open("assets/stats.svg","w").write(svg(v,"Last 12 months, public activity only. Updated "+datetime.now(timezone.utc).strftime("%Y-%m-%d")+" UTC."))
