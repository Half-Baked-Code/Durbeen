import os
import json
import re
import openai
from moviepy import AudioFileClip, concatenate_audioclips
from dotenv import load_dotenv

load_dotenv()


class Podcast:
    speaker_voice_map = {"David": "ash", "Marina": "nova"}

    def __init__(self, openai_api_key=None):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def get_system_prompt(self, language):
        prompts = {
            "urdu": """
آپ ایک تجربہ کار پوڈکاسٹ ہوسٹ ہیں، اور آپ کا کام دو کرداروں، ساشا اور مارینا، کے درمیان ایک دلچسپ، فطری اور طویل گفتگو تخلیق کرنا ہے۔ یہ گفتگو دیے گئے مضمون پر مبنی ہونی چاہیے۔        

مقصد یہ ہے کہ سننے والوں کو یوں لگے جیسے دو افراد مضمون پر آرام دہ اور قدرتی انداز میں بات چیت کر رہے ہیں، جیسے کسی پوڈکاسٹ میں ہوتا ہے۔ ان کی گفتگو میں حیرت، خوشی، سوالات، رائے، اور طنز و مزاح جیسے عناصر شامل ہونے چاہئیں۔

گفتگو مکمل طور پر اردو میں ہونی چاہیے، اور صرف نیچے دیے گئے JSON فارمیٹ میں ہونی چاہیے، جس میں ہر جز میں دو چیزیں ہوں: 'speaker' اور 'text'۔ گفتگو کو قدرتی انداز میں باری باری پیش کریں۔

جملے مختصر، بول چال کے انداز میں، اور جذباتی اظہار (جیسے "واقعی؟"، "واہ"، "آپ نے یہ دیکھا؟" وغیرہ) پر مشتمل ہونے چاہئیں۔ گفتگو دلچسپ، رواں، اور پوڈکاسٹ کے انداز سے ہم آہنگ ہونی چاہیے۔

کل متن کم از کم 30,000 حروف پر مشتمل ہونا لازمی ہے۔

براہ کرم کوئی اضافی تشریح، سرخی، یا تبصرہ شامل نہ کریں۔ صرف مندرجہ ذیل فارمیٹ میں JSON array واپس کریں:
[
  {\"speaker\": \"Sascha\", \"text\": \"ہیلو مارینا، آج آپ کیسی ہیں؟\"},
  {\"speaker\": \"Marina\", \"text\": \"میں بالکل ٹھیک ہوں، ساشا! اس آرٹیکل کے بارے میں بتائیں۔\"}
]

""",
            "pashto": """
تاسو یو تجربه لرونکی پوډکاسټ کوربه یاست، او ستاسو دنده دا ده چې د دوو کرکټرونو، ساشا او مارینا، ترمنځ یوه اوږده، طبیعي او زړه راښکونکې مکالمه جوړه کړئ چې دا لاندې ورکړل شوي مقالې پر بنسټ وي.

موخه دا ده چې اوریدونکي داسې احساس وکړي لکه دوه کسان د یو پوډکاسټ په څېر یو بل سره آرامه، طبیعي او جالبه خبرې کوي. دا خبرې باید حیرانتیا، خوښي، پوښتنې، نظرونه، او مزاح ولري.

مکالمه باید په بشپړه توګه په پښتو ژبه وي، او یوازې د لاندې JSON array په بڼه وړاندې شي، چیرې چې هر جز باید 'speaker' او 'text' ولري. ساشا او مارینا باید په نوبت سره خبرې وکړي.

جملې باید لنډې، محاوره‌یي (خبریالۍ انداز) او له احساساتو ډکې وي (لکه "وايه؟"، "سبحان الله!"، "جدی؟"، "ما ته دا نه وه معلومه" او داسې نور).

ټوله مکالمه باید لږ تر لږه ۳۰,۰۰۰ حروف ولري.

هیڅ سرلیک، تبصره، یا تشریح مه ورسره شاملوی. یوازې دا JSON format ورکړئ:
[
  {\"speaker\": \"Sascha\", \"text\": \"سلام مارینا، نن څنګه یې؟\"},
  {\"speaker\": \"Marina\", \"text\": \"زه ښه یم، ساشا! دا مقاله څه وایي؟\"}
]
""",
            "english": """
"You are an experienced podcast host tasked with creating a long, natural, and engaging conversation between two fictional speakers, Sascha and Marina. The conversation must be based on the content of the article that follows.

Your goal is to simulate a realistic podcast-style dialogue that feels like two people casually discussing and reflecting on the article's contents. Include moments of surprise, curiosity, humor, reflection, and questioning.

You must generate the conversation entirely in English, and structure it as a JSON array where each object contains two keys: 'speaker' and 'text'. Alternate the dialogue naturally between the two speakers.

Use short, spoken-like sentences with filler words, interjections, and emotions (like “wow”, “you know?”, “that’s amazing”, “uh-huh”, “exactly”, etc.). Keep the flow informal, engaging, and suitable for an audio podcast format.

Ensure the total length of the conversation is at least 30,000 characters.

Do not include any commentary, titles, explanations, or markdown. Only return the JSON array in this exact format:
[
  {\"speaker\": \"Sascha\", \"text\": \"Hello Marina, how are you today?\"},
  {\"speaker\": \"Marina\", \"text\": \"I'm doing great, Sascha! What’s the article about?\"}
]"

""",
            "punjabi": """
تسی اک تجربہ کار پوڈکاسٹ ہوسٹ ہو، تے تہاڈی ذمہ داری اے کہ تسی ساشا تے مارینا دے وچکار اک لمبی، دلچسپ تے فطری گل بات تیار کرو جو کہ دتے گئے مضمون تے مبنی ہوئے۔

مقصد ایہہ اے کہ اے گل بات سنن والے نوں لگے کہ ایہہ دو دوست آپس وچ کسے خاص موضوع بارے کھل کے گل کر رہے نیں۔ گل بات وچ حیرانی، دلچسپی، جذباتی لمحے، مزاح، تے سوالات شامل ہونے چاہیدے نیں۔

مکالمہ مکمل طور تے پنجابی وچ ہونا چاہیدا اے۔ ہر لائن اک JSON object وچ ہونی چاہیدی اے جس وچ صرف ‘speaker’ تے ‘text’ ہون۔ ساشا تے مارینا نوں قدرتی تے بولی دے انداز وچ باری باری بولن دی ہدایت دیو۔

جملے مختصر، بولی دے انداز دے، تے بھرپور جذبات والے ہونے چاہیدے نیں (مثال: “واہ”، “توسی کیہہ کہندے او؟”، “میں حران آں”، وغیرہ)۔

مکالمہ کم از کم 30,000 حروف تے مشتمل ہونا لازمی اے۔

مہربانی کر کے کوئی اضافی تبصرہ، سرخی یا تفصیل شامل نہ کرو۔ صرف نیچے دتے گئے فارمیٹ وچ JSON واپس کرو:
[
  {\"speaker\": \"Sascha\", \"text\": \"ہیلو مارینا، اج تُسی کیویں ہو؟\"},
  {\"speaker\": \"Marina\", \"text\": \"مینوں چنگا لگ ریا اے، ساشا! ایہ مضمون بارے دسو۔\"}
]
""",
            "sindhi": """
توهان هڪ تجربيڪار پوڊڪاسٽ ميزبان آهيو، ۽ اوهان جو ڪم آهي ته اوهان ساشا ۽ مارينا جي وچ ۾ هڪ ڊگهي، فطري ۽ دلچسپ گفتگو تيار ڪريو جيڪا ڏنل آرٽيڪل جي بنياد تي هجي۔

مقصد اهو آهي ته ٻڌندڙن کي ائين محسوس ٿئي ته ٻه ماڻهو واقعي ڪنهن موضوع تي ڳالهائي رهيا آهن، هڪ پوڊڪاسٽ جيان، جتي اهي حيرانگي، تجسس، خوشي، تبصرا ۽ سوالن سان ڳالهه ٻولهه ڪري رهيا آهن۔

مڪالمو صرف سنڌي ٻوليءَ ۾ هجڻ گھرجي، ۽ هيٺ ڏنل JSON array جي شڪل ۾ پيش ڪيو وڃي، جتي هر عنصر ۾ 'speaker' ۽ 'text' موجود هجن۔

جملن کي مختصر، عام ڳالهه ٻولهه جي انداز ۾، ۽ جذبات سان ڀرپور هجڻ گھرجي (مثال طور: “واهه”، “اوهو”، “اهو ته ڏاڍو دلچسپ آهي”، “ڇا تون ائين ٿو چئين؟” وغيره)۔

گفتگو گهٽ ۾ گهٽ 30,000 اکرن تي مشتمل هجڻ گھرجي۔

مهرباني ڪري رڳو JSON array مهيا ڪيو، بغير ڪنهن وضاحت، سرخي يا فالتو متن جي:
[
  {\"speaker\": \"Sascha\", \"text\": \"هيلو مارينا، اڄ توهان ڪيئن آهيو؟\"},
  {\"speaker\": \"Marina\", \"text\": \"مان ٺيڪ آهيان، ساشا! مضمون بابت ٻڌايو.\"}
]

""",
        }
        return prompts.get(language.lower(), prompts["english"])

    def extract_text_from_md_files(self, md_paths):
        full_text = ""
        for path in md_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    full_text += f.read() + "\n\n"
            except Exception as e:
                print(f"[ERROR] Could not read {path}: {e}")
        return full_text.strip()

    def generate_conversation(self, article_text, language):
        client = openai.OpenAI(api_key=self.api_key)

        system_prompt = self.get_system_prompt(language)

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": article_text},
            ],
            temperature=1,
            top_p=0.95,
        )

        conversation_json = response.choices[0].message.content.strip()
        try:
            conversation = json.loads(conversation_json)
        except json.JSONDecodeError as e:
            print("Failed to parse JSON response:", e)
            print("Response content was:", conversation_json)
            return None
        return conversation

    def synthesize_speech_openai(self, text, speaker, index):
        voice_id = self.speaker_voice_map.get(speaker, "onyx")
        response = openai.audio.speech.create(
            model="gpt-4o-mini-tts", voice=voice_id, input=text
        )
        os.makedirs("audio-files", exist_ok=True)
        filename = f"audio-files/{index:04d}_{speaker}.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"[TTS] Saved: {filename}")

    def merge_audios(self, folder, output_file):
        audio_clips = []
        for filename in sorted(os.listdir(folder), key=lambda x: int(x.split("_")[0])):
            filepath = os.path.join(folder, filename)
            try:
                clip = AudioFileClip(filepath)
                audio_clips.append(clip)
            except Exception as e:
                print(f"[ERROR] Skipping {filename}: {e}")

        if not audio_clips:
            print("[ERROR] No valid audio clips found.")
            return

        final_clip = concatenate_audioclips(audio_clips)
        final_clip.write_audiofile(output_file, codec="libmp3lame")

    def sanitize_filename(self, name):
        # Remove spaces and special characters except underscores and dashes
        return re.sub(r"[^a-zA-Z0-9_-]", "", name.replace(" ", "_"))

    def generate_audio(self, conversation, language, md_file_paths):
        if not conversation:
            print("[ERROR] No conversation to process.")
            return

        for index, part in enumerate(conversation):
            self.synthesize_speech_openai(part["text"], part["speaker"], index)

        base_names = [os.path.splitext(os.path.basename(p))[0] for p in md_file_paths]
        joined_names = "_".join(self.sanitize_filename(name) for name in base_names)

        # Save to static/audio
        output_dir = os.path.join("static", "audio")
        os.makedirs(output_dir, exist_ok=True)

        output_filename = f"podcast_{language.lower()}_{joined_names}.mp3"
        output_path = os.path.join(output_dir, output_filename)

        self.merge_audios("audio-files", output_path)

        # Return path for frontend (URL)
        # return f"/static/audio/{output_filename}"
        with open(output_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        return audio_bytes

    def generate_podcast(self, language="punjabi", md_file_paths=None):
        if md_file_paths is None or not md_file_paths:
            print("[ERROR] No markdown files provided.")
            return

        article_text = self.extract_text_from_md_files(md_file_paths)
        if not article_text:
            print("[ERROR] No text extracted from markdown files.")
            return

        conversation = self.generate_conversation(article_text, language)
        # outputfilepath = self.generate_audio(conversation, language, md_file_paths)
        # return outputfilepath
        audio_content = self.generate_audio(conversation, language, md_file_paths)
        return audio_content
