# AIOS-node Project Bootstrap

## Repository name

`AIOS-node`

Recommended GitHub owner: the same owner that currently hosts AIOS-renew, unless the Human
chooses otherwise.

## Initial repository visibility

For the source repository itself, public or private is a Human product/governance choice.

A future persistent self-hosted remote-control surface should be isolated into a private
control plane rather than exposing the mobile runner to untrusted public workflow execution.

## Initial commit

N0 consists only of governance/bootstrap documentation.

Do not add production host code in the same commit.

Suggested commit message:

```text
governance: establish AIOS-node constitutional boundary
```

## Local bootstrap commands

After creating an empty GitHub repository named `AIOS-node`:

```powershell
Set-Location "C:\TOOL\Projects"
git clone <AIOS-node repository clone URL>
Set-Location ".\AIOS-node"
```

Copy the bootstrap package contents into the repository, then:

```powershell
git add README.md docs .gitignore
git commit -m "governance: establish AIOS-node constitutional boundary"
git push -u origin main
```

## ChatGPT Project setup

Create a separate ChatGPT Project named:

`AIOS-node`

Use `docs/CHATGPT_PROJECT_CONTRACT.md` as the durable project contract.

At the start of a fresh work context the Brain should:
1. read the Project Contract;
2. read the Node Constitution;
3. read the Boundary;
4. read current main SHA;
5. read the active Roadmap;
6. determine the highest authored Node TASK and latest published Node implementation;
7. audit proposed work for overlap with AIOS-renew before authoring any TASK.

## Next engineering action after N0

Author `NODE-001` for N1 Mi 10 Pro Host Preflight.

Do not implement persistent service, GitHub Actions wakeup, request journal, or multi-node
logic before the N1/N2/N3 gates prove the basic host and AIOS compatibility boundary.
