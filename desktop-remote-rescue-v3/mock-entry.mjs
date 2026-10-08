// A mock of the official package's two interfaces: stdio MCP and remote CLI.
// It does not make network requests or use credentials.
const mode=process.argv[2]||"mcp";
const scenario=process.env.RESCUE_MOCK_SCENARIO||"online";
if(mode==="remote"){
 if(scenario==="auth"){
  console.log("Verification code: FAKE-CODE");
  console.log("Please open browser and authorize this device");
  setInterval(()=>{},1000);
 }else if(scenario==="hang"){
  console.log("Starting MCP Device...");
  console.log("Connecting to Local Desktop Commander MCP using: fixture");
  setInterval(()=>{},1000);
 }else if(scenario==="crash"){
  console.error("Simulated connection failure");
  process.exit(19);
 }else{
  console.log("Starting MCP Device...");
  setTimeout(()=>{
   console.log("Desktop Commander Remote is connected");
   console.log("Status: Online");
  },40);
  setInterval(()=>{},1000);
 }
}else if(mode==="--help"){
 console.log("Desktop Commander Remote help --debug --logout");
 process.exit(0);
}else{
 let input="";
 process.stdin.on("data",d=>{
  input+=d.toString("utf8");
  while(input.includes("\n")){
   const at=input.indexOf("\n"),line=input.slice(0,at).trim();input=input.slice(at+1);
   if(!line)continue;
   try{
    const msg=JSON.parse(line);
    if(msg.method==="initialize"){
      console.log(JSON.stringify({jsonrpc:"2.0",id:msg.id,result:{protocolVersion:"2025-03-26",capabilities:{tools:{}},serverInfo:{name:"fixture",version:"1"}}}));
    }else if(msg.method==="tools/list"){
      console.log(JSON.stringify({jsonrpc:"2.0",id:msg.id,result:{tools:[{name:"read_file",description:"fixture",inputSchema:{type:"object"}}]}}));
    }
   }catch(e){console.error("Malformed MCP input");}
  }
 });
}
