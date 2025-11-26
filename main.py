import asyncio
import components.main_window as cmw
import scripts.piano as pion

async def main():
    piano = pion.initPianoApp()
    await cmw.initWindow("Piano App", 800, 400, False, 60, piano=piano)

if __name__ == "__main__":
    asyncio.run(main())
