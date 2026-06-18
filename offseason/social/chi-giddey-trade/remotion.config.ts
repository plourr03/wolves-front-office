import { Config } from "@remotion/cli/config";

// PNG frames give accurate colors for charts. Overwrite lets re-renders replace
// the previous file without prompting.
Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);
