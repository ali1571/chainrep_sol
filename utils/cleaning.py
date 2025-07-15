import json
modifiedLines = []
with open('X:\\code\\chainrep_sol\\metrics\\kakashiUTTnames', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            line = line.replace('[','')
            line = line.replace('{', '')
            line = line.replace(']', '')
            line = line.replace('}', '')
            line = line.replace('"', '')
            line = line.replace(',', '')
            modifiedLines.append(line)
            print(line)


print(modifiedLines)
with open('UTT_mint_names', 'w') as f:
    f.write("kakashi Unique Tokens Traded\n")
    for lines in modifiedLines:
        f.write(lines + '\n')

#with open('X:\code\chainrep_sol\metrics\kakashiUTTnames', 'w') as f:
    