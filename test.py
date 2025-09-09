# Importing library
import qrcode

# Data to be encoded
data = 'bc1q33wqu54wauuf4eg4j93z0upx2hlrut4hq7qafc'

# Encoding data using make() function
img = qrcode.make(data)

# Saving as an image file
img.save('bitcoin.svg')