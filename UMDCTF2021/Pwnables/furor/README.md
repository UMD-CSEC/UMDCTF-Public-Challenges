# [RPi Zero] Furor

Why are we pwning raspberry pi's? I thought ARM is more secure that Intel... 

Both files are not required to download!

```
bootable-rpi0-phys-furor.img -- bootable image complete with rpi boot binaries/kernel, write-ready to sd card, use standard UART pins
kernel-rpi0-qemu-furor.img -- only kernel image ready for QEMU v5, load address differs from physical pi load address
```

## Helpful things

`qemu-system-arm -M raspi0 -kernel $(KERN).img -serial null -serial stdio` - run kernel in QEMU v5

[BCM2835 datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/502533/BOARDCOM/BCM2835.html)


- `Primary Author` -- WittsEnd2
- `Secondary Author` -- drkmrin78
- `Difficulty` -- 4/10
- `Flag` -- 1c7eb4dc439b1cbf00c7a0e793187979ee3fd5091cc9aff2f632ff9da3ec9851
