# copy-paste and REPLACE the contents of the "Interactive Console" of your dev app server with this file and click "Execute" -- Animesh
import os
import pprint

from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext import db

from models import CTConstituency
from models import CTCandidate
from google.appengine.ext import ndb

infos = [
(('hyd','Hyderabad','Andhra Pradesh'),[('Sama Krishna Reddy','Congress','UPA'), ('Asaduddin Owaisi','MIM',None)]),
(('malkajgiri','Malkajgiri','Andhra Pradesh'),[('Chandana Chakravarti','AAP',None), ('Sarvey Satyanarayana','Congress','UPA'),('Jaiprakash Narayan','LSP',None)]),
(('secunderabad','Secunderabad','Andhra Pradesh'),[('Chaya Ratan','AAP',None), ('Anjan Kumar Yadav','Congress','UPA')]),
(('vijaywada','Vijayawada','Andhra Pradesh'),[('Harmohinder Singh Sahani','AAP',None), ('Devineni Avinash','Congress','UPA')]),
(('gauhati','Gauhati','Assam'),[('Pranjal Bordoloy','AAP',None), ('Bijoya Chakravarty','BJP','NDA'), ('Manas Bora','Congress','UPA')]),
(('bhagalpur','Bhagalpur','Bihar'),[('Yogendra Mahto','AAP',None), ('Shahnawaz Hussain','BJP','NDA'), ('Bulo Mondal','RJD','UPA'),('Abu Qaiser','JDU',None)]),
(('darbhanga','Darbhanga','Bihar'),[('Prabhat Ranjan Das','AAP',None), ('Kirti Azad','BJP','NDA'), ('Ali Ashraf Fatmi','RJD','UPA'),('Sanjay Jha','JDU',None)]),
(('gopalganj','Gopalganj','Bihar'),[('Dr. Banwari Lal','AAP',None), ('Janak Chamar','BJP','NDA'), ('Dr Jyoti','Congress','UPA'), ('Anil Kumar','JDU',None)]),
(('hajipur','Hajipur','Bihar'),[('Sudhir Paswan','AAP',None), ('Ram Vilas Paswan','LJP','NDA'), ('Sanjeev Prasad Tony','Congress','UPA'), ('Ram Sunder Das','JDU',None)]),
(('madhepura','Madhepura','Bihar'),[('Anwar Alam','AAP',None), ('Vijay Kumar Kushwaha','BJP','NDA'), ('Pappu Yadav','RJD','UPA'),('Sharad Yadav','JDU',None)]),
(('patna-sahib','Patna Sahib','Bihar'),[('Parveen Amanullah','AAP',None), ('Shatrughna Sinha','BJP','NDA'), ('Kunal Singh','Congress','UPA'), ('Gopal Prasad Sinha','JDU',None)]),
(('pataliputra','Pataliputra','Bihar'),[('Kundan Singh','AAP',None), ('Ram Kripal Yadav','BJP','NDA'), ('Misa Bharti','RJD','UPA'),('Ranjan Prasad Yadav','JDU',None)]),
(('saran','Saran','Bihar'),[('Parmatma Singh','AAP',None), ('Rajiv Pratap Rudy','BJP','NDA'), ('Rabri Devi','RJD','UPA'),('Saleem Parvez','JDU',None)]),
(('chandigarh','Chandigarh','Chandigarh'),[('Gul Panag','AAP',None), ('Kirron Kher','BJP','NDA'), ('Pawan Kumar Bansal','Congress','UPA')	]),
(('bastar','Bastar','Chhattisgarh'),[('Soni Sori','AAP',None), ('Dinesh Kashyap','BJP','NDA'), ('Deepak Karma','Congress','UPA'), ('Manbodh Baghel','BSP',None),('Shankar Ram Thakur','SP',None),('Vimla Sori','CPI',None)]),
(('bilaspur','Bilaspur','Chhattisgarh'),[('Anand Mishra','AAP',None), ('Lakhanlal Sau','BJP','NDA'), ('Karuna Shukla','Congress','UPA'), ('Dhaniram Yadav','SP',None)]),
(('mahasamund','Mahasamund','Chhattisgarh'),[('Lakshman Masuriya','AAP',None), ('Chandulal Sahu','BJP','NDA'), ('Ajit Jogi','Congress','UPA')]),
(('raipur','Raipur','Chhattisgarh'),[('Sandip Tiwari','AAP',None), ('Ramesh Bais','BJP','NDA'), ('Satyanarayan Sharma','Congress','UPA'), ('Naveen Gupta','SP',None)]),
(('delhi-ne','Delhi (North East)','Delhi'),[('Anand Kumar','AAP',None), ('Manoj Tiwari','BJP','NDA'), ('Jai Prakash Aggarwal','Congress','UPA')	]),
(('delhi-e','Delhi (East)','Delhi'),[('Rajmohan Gandhi','AAP',None), ('Maheish Giri','BJP','NDA'), ('Sandeep Dikshit','Congress','UPA')	]),
(('delhi-new','New Delhi','Delhi'),[('Ashish Khetan','AAP',None), ('Meenakshi Lekhi','BJP','NDA'), ('Ajay Maken','Congress','UPA')]),
(('delhi-nw','Delhi (North West)','Delhi'),[('Rakhi Birla','AAP',None), ('Udit Raj','BJP','NDA'), ('Krishna Teerath','Congress','UPA')]),
(('delhi-w','Delhi (West)','Delhi'),[('Jarnail Singh','AAP',None), ('Pravesh Verma','BJP','NDA'), ('Mahabal Mishra','Congress','UPA')]),
(('delhi-s','Delhi (South)','Delhi'),[('Col Devendra Sehrawat','AAP',None), ('Ramesh Bidhuri','BJP','NDA'), ('Ramesh Kumar','Congress','UPA')]),
(('goa-south','Goa (South)','Goa'),[('Swati Kerkar','AAP',None), ('Narendra Sawaikar','BJP','NDA'), ('Aleix Reginald Lourenco','Congress','UPA'), ('Venus Habib','Independent',None)]),
(('ahmedabad-e','Ahmedabad (East)','Gujarat'),[('Dinesh Waghela','AAP',None), ('Paresh Rawal','BJP','NDA'), ('Himmatsingh Patel','Congress','UPA')]),
(('ahmedabad-w','Ahmedabad (West)','Gujarat'),[('Jayantilal Jethalal Mevada','AAP',None), ('Kiritbhai Solanki','BJP','NDA'), ('Ishwar Makwana','Congress','UPA')]),
(('vadodara','Vadodara','Gujarat'),[('Narendra Modi','BJP','NDA'), ('Madhusudan Mistry','Congress','UPA')]),
(('valsad','Valsad','Gujarat'),[('Govindbhai Patel','AAP',None), ('KC Patel','BJP','NDA'), ('Kishanbhai Patel','Congress','UPA')]),
(('hisar','Hisar','Haryana'),[('Yudhbir Singh Khyalia','AAP',None), ('Kuldeep Bishnoi','HJC','NDA'), ('Sampat Singh','Congress','UPA'), ('Mange Ram Prajapati','BSP',None)]),
(('hamirpur','Hamirpur','Himachal Pradesh'),[('Kamal Kant Batra','AAP',None), ('Anurag Thakur','BJP','NDA'), ('Rajinder Singh','Congress','UPA')]),
(('kangra','Kangra','Himachal Pradesh'),[('Rajan Sushant','AAP',None), ('Shanta Kumar','BJP','NDA'), ('Chander Kumar','Congress','UPA')]),
(('jammu','Jammu','Jammu and Kashmir'),[('Harbans Lal Bhagat','AAP',None), ('Jugal Kishore Sharma','BJP','NDA'), ('Madan Lal Sharma','Congress','UPA'), ('Yashpal Sharma','PDP',None)]),
(('udhampur','Udhampur','Jammu and Kashmir'),[('Jitendra Singh','BJP','NDA'), ('Ghulam Nabi Azad','Congress','UPA'), ('Arshid Malik (PDP), Bhim Singh (Panthers Party), Amrit Varsha','SP',None)]),
(('dumka','Dumka','Jharkhand'),[('Sahdeo Soren','AAP',None), ('Sunil Soren','BJP','NDA'), ('Shibu Soren','JMM','UPA'), ('Babulal Marandi','Jharkhand Vikas Morcha',None)]),
(('hazaribagh','Hazaribagh','Jharkhand'),[('Mithilesh Kumar Dangi','AAP',None), ('Jayant Sinha','BJP','NDA'), ('Saurabh Narayan Singh','Congress','UPA')]),
(('jamshedpur','Jamshedpur','Jharkhand'),[('Kumar Chandra Mardi','AAP',None), ('Vidhyut Mahato','BJP','NDA'), ('Niroop Kr Mahanty','JMM','UPA'), ('Ajay Kumar', 'Jharkhand Vikas Morcha',None), ('Daman Chandra Bhakt','BSP',None)]),
(('ranchi','Ranchi','Jharkhand'),[('Amanullah Aman','AAP',None), ('Ramtahal Chaudhary','BJP','NDA'), ('Subodh Kant Sahai','Congress','UPA')]),
(('bellary','Bellary','Karnataka'),[('Shivakumar Giriyappa Malagi','AAP',None), ('B. Sriramulu','BJP','NDA'), ('N. Y. Hanumanthappa','Congress','UPA')]),
(('bangalore-n','Bangalore (North)','Karnataka'),[('Babu Mathew','AAP',None), ('D. V. Sadanand Gowda','BJP','NDA'), ('C. Narayana Swamy','Congress','UPA'), ('Abdul Azeem','JDS',None)]),
(('bangalore-central','Bangalore (Central)','Karnataka'),[('V. Balakrishnan','AAP',None), ('P.C. Mohan','BJP','NDA'), ('Rizwan Arshad','Congress','UPA'), ('Nandini Alva','JDS',None)]),
(('dharwad','Dharwad','Karnataka'),[('Hemant Kumar','AAP',None), ('Prahlad Joshi','BJP','NDA'), ('Vinay Kulkarni','Congress','UPA'), ('Hanumantappa Bankapur','JDS',None)]),
(('mysore','Mysore','Karnataka'),[('Padmamma M.V.','AAP',None), ('Pratap Simha','BJP','NDA'), ('A.H. Vishwanath','Congress','UPA'), ('K Chandrashekharaiah','JDS',None)]),
(('shimoga','Shimoga','Karnataka'),[('G. Sridhara Kallahalla','AAP',None), ('B.S. Yeddyurappa','BJP','NDA'), ('Manjunath Bhandary','Congress','UPA')]),
(('thiruvananthapuram','Thiruvananthapuram','Kerala'),[('Ajit Joy','AAP',None), ('O. Rajagopal','BJP','NDA'), ('Shashi Tharoor','Congress','UPA'), ('Bennet Abraham','LDF',None)]),
(('chhindwara','Chhindwara','Madhya Pradesh'),[('Mahesh Dubey','AAP',None), ('Chandrabhan Singh','BJP','NDA'), ('Kamal Nath','Congress','UPA')]),
(('indore','Indore','Madhya Pradesh'),[('Anil Trivedi','AAP',None), ('Sumitra Mahajan','BJP','NDA'), ('Satyanarayan Patel','Congress','UPA')]),
(('bhopal','Bhopal','Madhya Pradesh'),[('Rachna Dheengra','AAP',None), ('Alok Sanjar','BJP','NDA'), ('P.C. Sharma','Congress','UPA')]),
(('gwalior','Gwalior','Madhya Pradesh'),[('Neelam Agrawal','AAP',None), ('Narendra Singh Tomar','BJP','NDA'), ('Ashok Singh','Congress','UPA')]),
(('vidisha','Vidisha','Madhya Pradesh'),[('Bhagawat Singh Rajput','AAP',None), ('Sushma Swaraj','BJP','NDA'), ('Lakshman Singh','Congress','UPA')]),
(('baramati','Baramati','Maharashtra'),[('Suresh Khopade','AAP',None), ('Mahadev Jankar','RS Paksha','NDA'), ('Supriya Sule','NCP','UPA')]),
(('nagpur','Nagpur','Maharashtra'),[('Anjali Damania','AAP',None), ('Nitin Gadkari','BJP','NDA'), ('Vilas Muttemwar','Congress','UPA')]),
(('nanded','Nanded','Maharashtra'),[('Narendra Singh Granthi','AAP',None), ('D. B. Patil','BJP','NDA'), ('Ashok Chavan','Congress','UPA')]),
(('nashik','Nashik','Maharashtra'),[('Vijay Pandhare','AAP',None), ('Hemant Godse','Shiv Sena','NDA'), ('Chhagan Bhujbal','NCP','UPA'), ('Pradeepchandra Pawar','MNS',None)]),
(('mumbai-n','Mumbai (North)','Maharashtra'),[('Satish Jain','AAP',None), ('Gopal Shetti','BJP','NDA'), ('Sanjay Nirupam','Congress','UPA')]),
(('mumbai-ne','Mumbai (North East)','Maharashtra'),[('Medha Patkar','AAP',None), ('Kirit Somaiyya','BJP','NDA'), ('Sanjay Dina Patil','NCP','UPA')]),
(('mumbai-nw','Mumbai (North West)','Maharashtra'),[('Mayank Gandhi','AAP',None), ('Gajanan Kirtikar','Shiv Sena','NDA'), ('Gurudas Kamat','Congress','UPA'), ('Mahesh Manjrekar','MNS',None), ('Rakhi Sawant','Independent',None)]),
(('mumbai-nc','Mumbai (North Central)','Maharashtra'),[('Phiroze Palkhivala','AAP',None), ('Poonam Mahajan','BJP','NDA'), ('Priya Dutt','Congress','UPA')]),
(('mumbai-sc','Mumbai (South Central)','Maharashtra'),[('Sundar Balakrishnan','AAP',None), ('Rahul Shewale','Shiv Sena','NDA'), ('Eknath Gaikwad','Congress','UPA'), ('Aditya Shirodkar','MNS',None)]),
(('mumbai-s','Mumbai (South)','Maharashtra'),[('Meera Sanyal','AAP',None), ('Arvind Sawant','Shiv Sena','NDA'), ('Milind Deora','Congress','UPA'), ('Bala Nandgaonkar','MNS',None)]),
(('pune','Pune','Maharashtra'),[('Subhash Ware','AAP',None), ('Anil Shirole','BJP','NDA'), ('Vishwajeet Kadam','Congress','UPA'), ('Deepak Paigude','MNS',None)]),
(('bhubaneshwar','Bhubaneswar','Odisha'),[('Bismaya Mohanty','AAP',None), ('Pruthwiraj Harichandan','BJP','NDA'), ('Bijaya Kumar Mohanty','Congress','UPA'), ('Prasanna Patsani','BJD',None),('Pramila Behera','CPIML',None),('Sanjay Hans','Aama Odisha',None)]),
(('puri','Puri','Odisha'),[('Nirada Baran Khuntia','AAP',None), ('Ashok Sahu','BJP','NDA'), ('Sucharita Mohanty','Congress','UPA'), ('Pinaki Mishra (BJD), Bhaskar Chandra Mohanty','BSP',None)]),
(('gurdaspur','Gurdaspur','Punjab'),[('Sucha Singh Chottepur','AAP',None), ('Vinod Khanna','BJP','NDA'), ('Pratap Singh Bajwa','Congress','UPA')]),
(('ajmer','Ajmer','Rajasthan'),[('Ajay Somani','AAP',None), ('Sanwarmal Jat','BJP','NDA'), ('Sachin Pilot','Congress','UPA')]),
(('jaipur','Jaipur','Rajasthan'),[('Virendra Singh','AAP',None), ('Ramcharan Vohra','BJP','NDA'), ('Mahesh Joshi','Congress','UPA')]),
(('jaipur-rural','Jaipur (Rural)','Rajasthan'),[('Anil Godara','AAP',None), ('Rajyavardhan Singh Rathore','BJP','NDA'), ('C.P. Joshi','Congress','UPA')]),
(('chennai-n','Chennai (North)','Tamilnadu'),[('S. Srinivason','AAP',None), ('M Soundrapandian','DMDK','NDA'), ('Biju Chacko','Congress','UPA'), ('T G Venkatesh Babu','AIDMK',None),('R Girirajan','DMK',None)]),
(('chennai-central','Chennai (Central)','Tamilnadu'),[('J Prabhakar','AAP',None), ('J K Raveendran','DMDK','NDA'), ('C. D. Meyyappan','Congress','UPA'), ('S R Vijayakumar','AIDMK',None),('Dayanidhi Maran','DMK',None)]),
(('chennai-s','Chennai (South)','Tamilnadu'),[('M. Jahir Hussain','AAP',None), ('La. Ganesan','BJP','NDA'), ('S.V. Ramani','Congress','UPA'), ('J Jeyavardhan','AIDMK',None),('TKS Elangovan','DMK',None)]),
(('coimbatore','Coimbatore','Tamilnadu'),[('Pon Chandran','AAP',None), ('C.P. Radhakrishnan','BJP','NDA'), ('R. Prabhu','Congress','UPA'), ('A P Nagarajan','AIDMK',None),('K Ganeshkumar','DMK',None)]),
(('kanyakumari','Kanyakumari','Tamilnadu'),[('S.P. Udayakumar','AAP',None), ('Pon Radhakrishnan','BJP','NDA'), ('H. Vasanthakumar','Congress','UPA'), ('D John Thangam','AIDMK',None),('FM Rajarathinam','DMK',None)]),
(('mayiladuturai','Mayiladuturai','Tamilnadu'),[('K Aghoram','PMK','NDA'), ('Mani Shankar Aiyyar','Congress','UPA'), ('R.K. Bharathi Mohan','AIDMK',None)]),
(('sinaganga','Sivaganga','Tamilnadu'),[('Thamil Arima','AAP',None), ('H. Raja','BJP','NDA'), ('Karthi Chidambaram','Congress','UPA'), ('P R Senthilnathan','AIDMK',None),('S Durairaj','DMK',None)]),
(('haridwar','Haridwar','Uttarakhand'),[('Kanchan C Bhattacharya','AAP',None), ('Ramesh Pokhriyal','BJP','NDA'), ('Nishank	Renuka Rawat','Congress','UPA'), ('Haji Mohammed Islam','BSP',None),('Anita Saini','SP',None)]),
(('allahabad','Allahabad','Uttar Pradesh'),[('Adarsh Shastri','AAP',None), ('Shyama Charan Gupta','BJP','NDA'), ('Nand Copal Gupta','Congress','UPA'), ('Keshari Devi Patel','BSP',None),('Revati Raman Singh','SP',None)]),
(('amethi','Amethi','Uttar Pradesh'),[('Kumar Vishwas','AAP',None), ('Smriti Irani','BJP','NDA'), ('Rahul Gandhi','Congress','UPA'), ('Dharmendra Pratap Singh','BSP',None)]),
(('agra','Agra','Uttar Pradesh'),[('Ravindra Singh','AAP',None), ('Ram Shankar Katheriya','BJP','NDA'), ('Upendra Singh Jatav','Congress','UPA'), ('Narayan Singh','BSP',None),('Mahraj Singh Dhangar','SP',None)]),
(('azamgarh','Azamgarh','Uttar Pradesh'),[('Rajesh Yadav','AAP',None), ('Ramakant Yadav','BJP','NDA'), ('Arvind Jaiswal','Congress','UPA'), ('Shah Alam','BSP',None),('Mulayam Singh Yadav','SP',None)]),
(('baghpat','Baghpat','Uttar Pradesh'),[('Soumendra Dhaka','AAP',None), ('Satyapal Singh','BJP','NDA'), ('Ajit Singh','RLD','UPA'), ('Prashant Chaudhary','BSP',None)]),
(('deoria','Deoria','Uttar Pradesh'),[('Arun Kumar Tripathi','AAP',None), ('Kalraj Mishra','BJP','NDA'), ('Sabha Kunwar Kushwaha','Congress','UPA'), ('Niyaz Khan','BSP',None),('Baleshwar Yadav','SP',None)]),
(('jhansi','Jhansi','Uttar Pradesh'),[('Archna Gupta','AAP',None), ('Uma Bharti','BJP','NDA'), ('Pradeep Jain Aditya','Congress','UPA'), ('Anuradha Sharma','BSP',None),('Chandrapal Singh Yadav','SP',None)]),
(('gautam-buddha-nagar','Gautam Buddha Nagar','Uttar Pradesh'),[('KP Singh','AAP',None), ('Mahesh Sharma','BJP','NDA'), ('Narinder Singh Bhati','SP',None),('Satish Awana','BSP',None)]),
(('ghaziabad','Ghaziabad','Uttar Pradesh'),[('Shazia Ilmi','AAP',None), ('Gen V. K. Singh','BJP','NDA'), ('Raj Babbar','Congress','UPA'), ('Mukul Upadhyay','BSP',None),('Sudhan Rawat','SP',None)]),
(('gorakhpur','Gorakhpur','Uttar Pradesh'),[('Prof. Radhey Mohan Mishra','AAP',None), ('Yogi Aditya Nath','BJP','NDA'), ('Ashtabhuja Tiwari','Congress','UPA'), ('Ram Bhual Nishad','BSP',None),('Rajmati Nishad','SP',None)]),
(('meerut','Meerut','Uttar Pradesh'),[('Himanshu Singh','AAP',None), ('Rajendra Agrawal','BJP','NDA'), ('Naghma	Haji','Congress','UPA'), ('Shahid Ikhlaq','BSP',None),('Shahid Manzoor','SP',None)]),
(('muzaffarnagar','Muzaffarnagar','Uttar Pradesh'),[('Mohammed Yamin','AAP',None), ('Sanjeev Baliyan','BJP','NDA'), ('Pankaj Aggarwal','Congress','UPA'), ('Qadir Rana','BSP',None),('Gaurav Swarup','SP',None)]),
(('raebareli','Rae Bareli','Uttar Pradesh'),[('Justice Fakhruddin','AAP',None), ('Ajay Aggarwal','BJP','NDA'), ('Sonia Gandhi','Congress','UPA'), ('Pravesh Singh','BSP',None)]),
(('sultanpur','Sultanpur','Uttar Pradesh'),[('Shailendra Pratap Singh','AAP',None), ('Varun Gandhi','BJP','NDA'), ('Amita Sanjay Singh','Congress','UPA'), ('Pawan Pandey','BSP',None),('Shakil Ahmed','SP',None)]),
(('darjeeling','Darjeeling','West Bengal'),[('S. S. Ahluwalia','BJP','NDA'), ('Sujoy Ghatak','Congress','UPA'), ('Bhaichung Bhutia','AITMC',None), ('Saman Pathak','CPI(M)',None)]),
(('dumdum','Dum Dum','West Bengal'),[('Tapan Sikdar','BJP','NDA'), ('Dhananjay Moitra','Congress','UPA'), ('Saugata Roy','AITMC',None), ('Asim Dasgupta','CPI(M)',None)]),
(('kolkata-dakshin','Kolkata (Dakshin)','West Bengal'),[('Mudar Pathreya','AAP',None), ('Tathagata Roy','BJP','NDA'), ('Mala Roy','Congress','UPA'),('Subrata Bakshi','AITMC',None), ('Nandini Mukherjee','CPI(M)',None)]),
(('kolkata-uttar','Kolkata (Uttar)','West Bengal'),[('Alok Chaturvedi','AAP',None), ('Rahul Sinha','BJP','NDA'), ('Somendra Nath Mitra','Congress','UPA'), ('Sudip Bandopadhyaya','AITMC',None), ('Rupa Bagchi','CPI(M)',None)]),
(('srerampur','Srerampur','West Bengal'),[('Bappi Lahiri','BJP','NDA'), ('Abdul Mannan','Congress','UPA'), ('Kalyan Banerjee','AITMC',None),('Tirthankar Roy','CPI(M)',None)]),
(('amritsar','Amritsar','Punjab'),[('Dajit Singh','AAP',None), ('Arun Jaitley','BJP','NDA'), ('Amrinder Singh','Congress','UPA')]),
(('bangalore-s','Bangalore (South)','Karnataka'),[('Nina Nayak','AAP',None), ('Ananth Kumar','BJP','NDA'), ('Nandan Nilekani','Congress','UPA'),('Pramod Muthalik','Independent',None)]),
(('guna','Guna','Madhya Pradesh'),[('Shailendra Singh Kushwaha','AAP',None), ('Jaibhan Singh Pawaiyya','BJP','NDA'), ('Jyotiradiya Scindia','Congress','UPA')]),	
(('barmer','Barmer','Rajasthan'),[('Mangilal Gaur','AAP',None), ('Col. Sonaram Choudhary','BJP','NDA'), ('Harish Choudhary','Congress','UPA'),('Jaswant Singh','Independent',None)]),
(('gandhinagar','Gandhinagar','Gujarat'),[('Riturajbhai Maheta','AAP',None), ('L.K. Advani','BJP','NDA'), ('Kirit Patel','Congress','UPA')]),
(('kanpur-urban','Kanpur (Urban)','Uttar Pradesh'),[('Mahmood Husain Rehmani','AAP',None), ('Murali Manohar Joshi','BJP','NDA'), ('Sriprakash Jaiswal','Congress','UPA'),('Salim Ahmed','BSP',None),('Surendra Mohan Agarwal','SP',None)]),
(('gurgaon','Gurgaon','Haryana'),[('Yogendra Yadav','AAP',None), ('Rao Indrajeet Singh','BJP','NDA'), ('Rao Dharampal','Congress','UPA')]),
(('delhi-chandnichowk','Chandni Chowk','Delhi'),[('Ashutosh Gupta','AAP',None), ('Dr. Harsh Vardhan','BJP','NDA'), ('Kapil Sibal','Congress','UPA')]),
(('varanasi','Varanasi','Uttar Pradesh'),[('Arvind Kejriwal','AAP',None), ('Narendra Modi','BJP','NDA'), ('Ajay Rai','Congress','UPA'), ('Vijay Jaiswal','BSP',None),('Kailash Chaurasia','SP',None)]),
(('lucknow','Lucknow','Uttar Pradesh'),[('Jaaved Jaaferi','AAP',None), ('Rajnath Singh','BJP','NDA'), ('Rita Bahuguna Joshi','Congress','UPA'), ('Nakul Dubey','BSP',None),('Ashok Bajpai','SP',None)]),
]

for (cons,candidates) in infos:
    (slug,name,state) = cons
    print slug, name, state
    print "candidates"
    candidate_list = []
    for (cname, cparty, ccoalition) in candidates:
        print "   ", cname, cparty, ccoalition
        candidate = CTCandidate(name=cname,party=cparty, coalition=ccoalition)
        candidate.put()
        candidate_list.append(candidate.key)
    conskey = ndb.Key(CTConstituency, slug)
    cons = CTConstituency(key=conskey,name=name,state=state, candidates=candidate_list)
    cons.put()
    

