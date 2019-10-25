       identification division.
       program-id. otp.
      
       environment division.
       input-output section.
       file-control.
           select key-file assign to 'key.txt'
           organization line sequential.
      
       data division.
       file section.
       fd key-file.
       01 key-data pic x(50).
      
       working-storage section.
       01 ws-flag pic x(1).
       01 ws-key pic x(50).
       01 ws-parse.
           05 ws-parse-data pic S9(9).
       01 ws-xor-len pic 9(1) value 1.
       77 ws-ctr pic 9(1).
      
       procedure division.
           open input key-file.
           read key-file into ws-key end-read.
      
           display 'Enter your message to encrypt:'.
           move 1 to ws-ctr.
           perform 50 times
               call 'getchar' end-call
               move return-code to ws-parse
               move ws-parse to ws-flag

               call 'CBL_XOR' using ws-key(ws-ctr:1) ws-flag by value
               ws-xor-len end-call

               display ws-flag with no advancing
               add 1 to ws-ctr end-add
           end-perform.
      
       cleanup.
           close key-file.
           goback.
       end program otp.

