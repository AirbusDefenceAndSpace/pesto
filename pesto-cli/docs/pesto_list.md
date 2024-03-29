# pesto list

The `pesto list` command provides the list of available build docker images in the pesto workspace.

```bash
pesto list
```

!!! Example

    It results the available builds list such as:
    
    ```
    ---------------------------------------------------------------------------------------------------------------------------
      ____  _____ ____ _____ ___        ____                              _                 __            _
     |  _ \| ____/ ___|_   _/ _ \   _  |  _ \ _ __ ___   ___ ___  ___ ___(_)_ __   __ _    / _| __ _  ___| |_ ___  _ __ _   _
     | |_) |  _| \___ \ | || | | | (_) | |_) | '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |  | |_ / _` |/ __| __/ _ \| '__| | | |
     |  __/| |___ ___) || || |_| |  _  |  __/| | | (_) | (_|  __/\__ \__ \ | | | | (_| |  |  _| (_| | (__| || (_) | |  | |_| |
     |_|   |_____|____/ |_| \___/  (_) |_|   |_|  \___/ \___\___||___/___/_|_| |_|\__, |  |_|  \__,_|\___|\__\___/|_|   \__, |
                                                                                  |___/                                 |___/
    -----  ProcESsing facTOry : 1.4.3     -------------------------------------------------------------------------------------
    
    Processing Factory repository path :
    
    list of available builds :
    
     algo-service:1.0.0.dev0 :
                pesto build algo-service:1.0.0.dev0
                 
     algo-service:1.0.0.dev0-stateful :
                pesto build algo-service:1.0.0.dev0-stateful
                      
    ```