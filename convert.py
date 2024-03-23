pins =  {
      1: '1C̅L̅R̅',
      2: '1D',
      3: '1CLK',
      4: '1P̅R̅E̅',
      5: '1Q',
      6: '1Q̅',
      7: '⏚',

      8:  '2C̅L̅R̅',
      9:  '2D',
      10: '2CLK',
      11: '2P̅R̅E̅',
      12: '2Q',
      13: '2Q̅',
      14:  '+',
    }


n = len(pins)
for i in range(n//2):
    print(f"{pins[i+1]:>4s}    {pins[n-i]:s}")
