param()

$ErrorActionPreference="Stop"
$Repo="Terminator364/P2PCR95"
$ArtifactName="P2PCR95-BETA02.1-WINDOWS"
$ReleaseTag="buildhub-inputs-v1"
$AssetName="P2PCR95-Agent-BETA02.1.exe"
$ExpectedSha="ce658b5d07abddd620802752cbfd00a38e60353852e736949102439e0134211c"

function Fail($Code,$Message){throw "[$Code] $Message"}

if(-not(Get-Command gh -ErrorAction SilentlyContinue)){Fail "GH_MISSING" "GitHub CLI is missing."}
& gh auth status -h github.com *> $null
if($LASTEXITCODE -ne 0){Fail "GH_AUTH" "GitHub CLI is not authenticated."}

$temp=Join-Path $env:TEMP ("mbh-input-"+[guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $temp|Out-Null

try{
  $asset=Join-Path $temp $AssetName

  & gh release view $ReleaseTag -R $Repo *> $null
  if($LASTEXITCODE -eq 0){
    try{
      & gh release download $ReleaseTag -R $Repo -p $AssetName -D $temp --clobber
      if($LASTEXITCODE -eq 0 -and (Test-Path $asset)){
        $sha=(Get-FileHash -Algorithm SHA256 $asset).Hash.ToLowerInvariant()
        if($sha -eq $ExpectedSha){
          Write-Host "DURABLE_INPUT_ALREADY_READY" -ForegroundColor Green
          return
        }
      }
    }catch{}
    Remove-Item $asset -Force -ErrorAction SilentlyContinue
  }

  $token=(& gh auth token).Trim()
  if(-not $token){Fail "GH_TOKEN" "Cannot read GitHub authentication token."}
  $headers=@{
    Authorization="Bearer $token"
    Accept="application/vnd.github+json"
    "X-GitHub-Api-Version"="2022-11-28"
  }

  $api="https://api.github.com/repos/$Repo/actions/artifacts?name=$ArtifactName&per_page=100"
  $listing=Invoke-RestMethod -UseBasicParsing -Headers $headers -Uri $api -Method Get
  $artifact=@($listing.artifacts|Where-Object{-not $_.expired}|Sort-Object created_at|Select-Object -Last 1)[0]
  if(-not $artifact){Fail "SOURCE_ARTIFACT_MISSING" "No non-expired $ArtifactName artifact exists."}

  $zip=Join-Path $temp "source.zip"
  Invoke-WebRequest -UseBasicParsing -Headers $headers -Uri $artifact.archive_download_url -OutFile $zip

  $extract=Join-Path $temp "extract"
  Expand-Archive -Path $zip -DestinationPath $extract -Force
  $source=Get-ChildItem $extract -Recurse -File -Filter $AssetName|Select-Object -First 1
  if(-not $source){Fail "SOURCE_EXE_MISSING" "$AssetName not found inside artifact."}

  Copy-Item $source.FullName $asset -Force
  $sha=(Get-FileHash -Algorithm SHA256 $asset).Hash.ToLowerInvariant()
  if($sha -ne $ExpectedSha){Fail "SOURCE_HASH_MISMATCH" "Expected $ExpectedSha but got $sha."}

  & gh release view $ReleaseTag -R $Repo *> $null
  if($LASTEXITCODE -eq 0){
    & gh release upload $ReleaseTag $asset -R $Repo --clobber
  }else{
    $notes="Durable non-secret BuildHub input migrated from verified BETA02.1 artifact. SHA256: $ExpectedSha. This asset is build provenance input, not a user release."
    & gh release create $ReleaseTag $asset -R $Repo --prerelease --latest=false --title "P2PCR95 BuildHub durable inputs" --notes $notes
  }
  if($LASTEXITCODE -ne 0){Fail "DURABLE_RELEASE_FAILED" "Could not create/upload durable input release asset."}

  Remove-Item $asset -Force
  & gh release download $ReleaseTag -R $Repo -p $AssetName -D $temp --clobber
  if($LASTEXITCODE -ne 0 -or -not(Test-Path $asset)){Fail "DURABLE_VERIFY_DOWNLOAD" "Could not redownload durable asset."}
  $verify=(Get-FileHash -Algorithm SHA256 $asset).Hash.ToLowerInvariant()
  if($verify -ne $ExpectedSha){Fail "DURABLE_VERIFY_HASH" "Durable release asset hash mismatch."}

  Write-Host "DURABLE_INPUT_MIGRATION_PASS" -ForegroundColor Green
}
finally{
  if(Test-Path $temp){Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue}
}
