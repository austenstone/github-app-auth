import { App } from "octokit";
import fs from "fs";

const APP_ID = process.env.GITHUB_APP_ID;
const PRIVATE_KEY = fs.existsSync("private-key.pem") ? fs.readFileSync("private-key.pem", "utf8") : process.env.GITHUB_PRIVATE_KEY;

const app = new App({
    appId: APP_ID,
    privateKey: PRIVATE_KEY.replace(/\\n/g, '\n'),
});

// Get the installation ID
let INSTALLATION_ID = process.env.GITHUB_INSTALLATION_ID;
if (!INSTALLATION_ID) {
    const res = await app.octokit.request("/app/installations")
    INSTALLATION_ID = res.data[0].id;
}
console.log('INSTALLATION_ID', INSTALLATION_ID)

// Authenticate as installation
const octokit = await app.getInstallationOctokit(INSTALLATION_ID);

const login = await octokit.graphql(`
query {
  viewer {
    login
  }
}
`)
console.log(login);

const meta = await octokit.request("GET /meta")
console.log(meta.data);