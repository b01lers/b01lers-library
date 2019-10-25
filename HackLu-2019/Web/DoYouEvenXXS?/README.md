Client-side bugs are the future of websec! Now that we're done matching this year's theme let's get right into business:

Our challenge has two different instances:
One instance is externally reachable. It has debugging capabilities, which means you can disable token checks via ?debug. Look at the challenge to know what that means. You can always check the X-Token-Validity header to see how you're doing.
The second instance is only internally reachable. It is used to verify your solutions and is only reachable via HTTP. Keep that in mind when submitting your exploit.

If you have any questions regarding the setup, feel free to ask in IRC. We want you to have fun with XSS! :-)
