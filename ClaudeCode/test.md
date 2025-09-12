$Env:ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
$Env:ANTHROPIC_AUTH_TOKEN="55d13bd21337470e885fed3c54603697.bYAofGaTfZCBZDF3"
% export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
% export ANTHROPIC_AUTH_TOKEN="55d13bd21337470e885fed3c54603697.bYAofGaTfZCBZDF3"

export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
setx ANTHROPIC_BASE_URL "https://open.bigmodel.cn/api/anthropic"
setx ANTHROPIC_AUTH_TOKEN "55d13bd21337470e885fed3c54603697.bYAofGaTfZCBZDF3"



启动claude交互界面
npx -y claude
在我的终端界面中，需要加上前缀npx，才可以执行claude的操作。
npx是全局可执行目录，没有这个的设置，则找不到可执行文件

jimeng
claude mcp add --transport http hans-m-yin-jimeng-mcp "https://server.smithery.ai/@Hans-M-Yin/jimeng-mcp/mcp?api_key=5697e93c-454a-4835-82fd-021c02b31cbe&profile=supposed-porpoise-fceen7"

飞书mcp的安装：
claude mcp add lark-mcp -- cmd /c "npx -y @larksuiteoapi/lark-mcp mcp -a cli_a84be40d90a0900c -s WQp51ZU1oRIzp2fUAEV3ReRv6NeCZmfm --oauth"

天气mcp的安装：
claude mcp add --transport http harun-guclu-weather-mcp "https://server.smithery.ai/@HarunGuclu/weather_mcp/mcp?api_key=5697e93c-454a-4835-82fd-021c02b31cbe&profile=supposed-porpoise-fceen7"

claude mcp add --transport http krieg-2065-firecrawl-mcp-server "你的Smithery中带密钥的URL"
claude mcp add --transport http krieg-2065-firecrawl-mcp-server "https://server.smithery.ai/@Krieg2065/firecrawl-mcp-server/mcp?api_key=5697e93c-454a-4835-82fd-021c02b31cbe&profile=supposed-porpoise-fceen7"
