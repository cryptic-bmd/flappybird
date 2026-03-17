import { toast } from "react-toastify";

export async function copyTextToClipboard(text: string, textName: string = "Text") {
  try {
    await navigator.clipboard.writeText(text);
    toast.success(`${textName} copied`, {
      style: {
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        borderRadius: "12px",
      },
      autoClose: 1000,
      hideProgressBar: true,
    });
    // showCopied = true;
    // setTimeout(() => (showCopied = false), 2000);
  } catch (e) {
    console.error('Failed to copy:', e);
    toast.error("Unable to copy address", {
      style: {
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        borderRadius: "12px",
      },
      autoClose: 1000,
      hideProgressBar: true,
    });
  }
}
