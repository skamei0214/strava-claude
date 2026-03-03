import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { execSync } from "child_process";
import { readFileSync } from "fs";
import { join } from "path";

const PROJECT_DIR = join(process.env.HOME, "projects/strava-claude");
const ACTIVITIES_FILE = join(PROJECT_DIR, "activities.txt");
const SYNC_SCRIPT = join(PROJECT_DIR, "strava_sync.py");

const server = new Server(
  { name: "strava", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "get_strava_activities",
      description:
        "Fetch the latest Strava training activities. Always call this at the start of a conversation to load fresh data before any analysis.",
      inputSchema: {
        type: "object",
        properties: {
          num_activities: {
            type: "number",
            description: "Number of recent activities to fetch (default: 20)",
          },
        },
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== "get_strava_activities") {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }

  try {
    const num = request.params.arguments?.num_activities ?? 20;

    // Run the sync script — updates activities.txt with fresh Strava data
    execSync(`python3 "${SYNC_SCRIPT}" ${num}`, {
      cwd: PROJECT_DIR,
      timeout: 60_000,
      stdio: "pipe",
    });

    const data = readFileSync(ACTIVITIES_FILE, "utf8");

    return {
      content: [{ type: "text", text: data }],
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error fetching Strava data: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
