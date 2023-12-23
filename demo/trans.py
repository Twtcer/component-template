# import asyncio  

# async def convert_audio(input_file, output_file):
#     cmd = f'ffmpeg -i {input_file} -f s16le -ac 1 -acodec pcm_s16le -ar 16000 {output_file}'
#     process = await asyncio.create_subprocess_shell(cmd)
#     await process.communicate()  

# if __name__ == "__main__":  
#     path = './wave/d72335d2bd8840f3b7be8222c4868df0' 
#     asyncio.run(convert_audio(f'{path}.mp3', f'{path}.pcm')) 


